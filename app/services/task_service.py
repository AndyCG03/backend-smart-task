from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.database_models import Task, TaskHistory, Category
from app.models.pydantic_models import TaskCreate
import logging

logger = logging.getLogger(__name__)

class TaskService:
    @staticmethod
    def _calcular_priority_level(urgency: Optional[str], impact: Optional[str], 
                               deadline: Optional[datetime], energy_required: Optional[str],
                               estimated_duration: Optional[int]) -> str:
        """
        Calcula el nivel de prioridad basado en reglas claras y transparentes.
        """
        # Valores por defecto
        urgency_val = urgency or "medium"
        impact_val = impact or "medium"
        energy_val = energy_required or "medium"
        
        # Puntuación base
        score = 0
        
        # 1. URGENCY E IMPACT (peso principal)
        urgency_weights = {"low": 1, "medium": 2, "high": 3}
        impact_weights = {"low": 1, "medium": 2, "high": 3}
        
        score += urgency_weights.get(urgency_val, 2)
        score += impact_weights.get(impact_val, 2)
        
        # 2. DEADLINE (peso moderado) - CORREGIDO
        if deadline:
            # Normalizar timezones
            if deadline.tzinfo is not None:
                now = datetime.now(timezone.utc)
                deadline_utc = deadline.astimezone(timezone.utc)
            else:
                now = datetime.now()
                deadline_utc = deadline
            
            # Calcular diferencia correctamente usando total_seconds
            time_until_deadline = deadline_utc - now
            total_seconds = time_until_deadline.total_seconds()
            
            if total_seconds < 0:
                # Tarea vencida
                score += 3
                logger.debug("⚠️ Tarea vencida - bonus +3")
            elif total_seconds <= 2 * 3600:  # 2 horas
                score += 2
                logger.debug("📅 Vence en 2 horas - bonus +2")
            elif total_seconds <= 24 * 3600:  # 24 horas
                score += 2
                logger.debug("📅 Vence hoy - bonus +2")
            elif total_seconds <= 3 * 24 * 3600:  # 3 días
                score += 1
                logger.debug("📅 Vence en 3 días - bonus +1")
        
        # 3. ENERGÍA REQUERIDA (ajuste menor)
        energy_adjustments = {"low": 1, "medium": 0, "high": -1}
        score += energy_adjustments.get(energy_val, 0)
        
        # 4. DURACIÓN ESTIMADA (ajuste menor)
        if estimated_duration and estimated_duration > 240:  # > 4 horas
            score -= 1
            logger.debug("⏱️ Tarea larga - penalización -1")
        
        # Determinar nivel de prioridad basado en puntuación
        logger.debug(f"🎯 Puntuación total calculada: {score}")
        
        if score >= 7:
            return "high"
        elif score >= 4:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _calcular_priority_score(priority_level: str, urgency: Optional[str], 
                               impact: Optional[str], deadline: Optional[datetime]) -> int:
        """
        Calcula el score numérico (1-100) basado en el nivel de prioridad y factores adicionales.
        """
        # Score base según nivel
        base_scores = {"low": 25, "medium": 50, "high": 75}
        score = base_scores.get(priority_level, 50)
        
        # Ajustes basados en urgencia e impacto dentro del mismo nivel
        if priority_level == "high":
            if urgency == "high" and impact == "high":
                score += 15
            elif urgency == "high" or impact == "high":
                score += 8
        elif priority_level == "medium":
            if urgency == "high" or impact == "high":
                score += 10
            elif urgency == "low" and impact == "low":
                score -= 10
        elif priority_level == "low":
            if urgency == "high" or impact == "high":
                score += 15
            elif urgency == "medium" or impact == "medium":
                score += 5
        
        # Ajuste por deadline muy próximo - CORREGIDO
        if deadline:
            if deadline.tzinfo is not None:
                now = datetime.now(timezone.utc)
                deadline_utc = deadline.astimezone(timezone.utc)
            else:
                now = datetime.now()
                deadline_utc = deadline
            
            total_seconds = (deadline_utc - now).total_seconds()
            hours_until = total_seconds / 3600
            
            if hours_until <= 2:  # 2 horas
                score = min(100, score + 20)
                logger.debug("🚨 Deadline en 2h - bonus +20")
            elif hours_until <= 24:  # 24 horas
                score = min(100, score + 10)
                logger.debug("⏰ Deadline en 24h - bonus +10")
        
        # Asegurar que esté en el rango 1-100
        final_score = max(1, min(100, score))
        logger.debug(f"📊 Score final calculado: {final_score}")
        
        return final_score

    @staticmethod
    def create_task_with_priority(db: Session, task_create: TaskCreate, user_id: UUID, category_id: Optional[UUID] = None):
        """Crear tarea con cálculo automático de prioridad usando solo reglas"""
        
        # Validar categoría si se proporciona
        if category_id:
            category = db.query(Category).filter(
                Category.id == category_id,
                Category.user_id == user_id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or doesn't belong to user"
                )

        # Preparar datos de la tarea
        task_data = task_create.dict()
        task_data['user_id'] = user_id
        if category_id:
            task_data['category_id'] = category_id
        
        # Calcular priority_level con reglas claras
        priority_level = TaskService._calcular_priority_level(
            urgency=task_create.urgency,
            impact=task_create.impact,
            deadline=task_create.deadline,
            energy_required=task_create.energy_required,
            estimated_duration=task_create.estimated_duration
        )
        
        # Calcular priority_score con reglas claras
        priority_score = TaskService._calcular_priority_score(
            priority_level=priority_level,
            urgency=task_create.urgency,
            impact=task_create.impact,
            deadline=task_create.deadline
        )
        
        # Asignar ambos valores
        task_data['priority_level'] = priority_level
        task_data['priority_score'] = priority_score
        
        logger.info(f"✅ Tarea creada - Level: {priority_level}, Score: {priority_score}")
        
        # Crear la tarea
        db_task = Task(**task_data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Registrar en historial
        history_entry = TaskHistory(
            task_id=db_task.id,
            user_id=user_id,
            change_type='created',
            new_values={
                'title': db_task.title,
                'status': db_task.status,
                'description': db_task.description,
                'priority_level': db_task.priority_level,
                'priority_score': db_task.priority_score
            },
            change_description='Task created with rule-based priority calculation'
        )
        db.add(history_entry)
        db.commit()
        
        return db_task

    @staticmethod
    def create_task_with_history(db: Session, task_data: TaskCreate, user_id: UUID):
        """Crear tarea y registrar en historial (versión original)"""
        # Crear tarea
        db_task = Task(**task_data.dict(), user_id=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # Registrar en historial
        history_entry = TaskHistory(
            task_id=db_task.id,
            user_id=user_id,
            change_type='created',
            new_values={
                'title': db_task.title,
                'description': db_task.description,
                'status': db_task.status
            },
            change_description='Task created'
        )
        db.add(history_entry)
        db.commit()
        
        return db_task

    @staticmethod
    def update_task_status(db: Session, task_id: UUID, user_id: UUID, new_status: str, old_status: str):
        """Actualizar estado de tarea y registrar en historial"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = new_status
            db.commit()
            
            # Registrar cambio en historial
            history_entry = TaskHistory(
                task_id=task_id,
                user_id=user_id,
                change_type='status_changed',
                old_values={'status': old_status},
                new_values={'status': new_status},
                change_description=f'Status changed from {old_status} to {new_status}'
            )
            db.add(history_entry)
            db.commit()
            
        return task

    @staticmethod
    def recalculate_task_priority(db: Session, task_id: UUID, user_id: UUID):
        """Recalcular prioridad de una tarea existente (útil si cambian los datos)"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Recalcular priority_level
        new_priority_level = TaskService._calcular_priority_level(
            urgency=task.urgency,
            impact=task.impact,
            deadline=task.deadline,
            energy_required=task.energy_required,
            estimated_duration=task.estimated_duration
        )
        
        # Recalcular priority_score
        new_priority_score = TaskService._calcular_priority_score(
            priority_level=new_priority_level,
            urgency=task.urgency,
            impact=task.impact,
            deadline=task.deadline
        )
        
        # Guardar cambios si son diferentes
        if (task.priority_level != new_priority_level or 
            task.priority_score != new_priority_score):
            
            old_level = task.priority_level
            old_score = task.priority_score
            
            task.priority_level = new_priority_level
            task.priority_score = new_priority_score
            db.commit()
            
            # Registrar en historial
            history_entry = TaskHistory(
                task_id=task_id,
                user_id=user_id,
                change_type='priority_updated',
                old_values={
                    'priority_level': old_level,
                    'priority_score': old_score
                },
                new_values={
                    'priority_level': new_priority_level,
                    'priority_score': new_priority_score
                },
                change_description='Priority recalculated based on rule changes'
            )
            db.add(history_entry)
            db.commit()
            
            logger.info(f"🔄 Prioridad recalculada: {old_level}({old_score}) -> {new_priority_level}({new_priority_score})")
        
        return task