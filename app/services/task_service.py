from uuid import UUID
from sqlalchemy.orm import Session
from app.models.database_models import Task, TaskHistory
from app.models.pydantic_models import TaskCreate

class TaskService:
    @staticmethod
    def create_task_with_history(db: Session, task_data: TaskCreate, user_id: UUID):
        """Crear tarea y registrar en historial"""
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