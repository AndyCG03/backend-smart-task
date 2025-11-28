# app/services/task_agent.py
import pandas as pd
from sklearn.linear_model import SGDRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
import joblib
from io import BytesIO
import traceback
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

from app.models.database_models import Task, TaskMLData, MLFeedback, AIModel


class TaskAgent:
    """
    Agente de priorización de tareas personalizado por usuario.
    Combina machine learning (SGDRegressor) y reglas heurísticas,
    con enriquecimiento de texto, post-procesamiento contextual,
    y reentrenamiento basado en feedback.
    """

    def __init__(self, db: Session, user_id: uuid.UUID = None):
        self.db = db
        self.user_id = user_id
        self.modelo = None
        # Vectorizador declarado pero no usado actualmente (reservado para features textuales futuras)
        self.vectorizador = TfidfVectorizer(max_features=50, stop_words='english')
        self.encoder_urgencia = LabelEncoder()
        self.encoder_impacto = LabelEncoder()
        self.encoder_energia = LabelEncoder()

        logger.info(f"🔄 Inicializando TaskAgent para usuario: {user_id}")
        self._cargar_modelo()

    def _cargar_modelo(self):
        """Carga el modelo ML más reciente y activo del usuario desde la base de datos."""
        try:
            logger.info("🔍 Buscando modelo ML en base de datos...")
            modelo_db = self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.is_active == True
            ).order_by(AIModel.trained_at.desc()).first()

            if modelo_db and modelo_db.model_data:
                logger.info(f"✅ Modelo encontrado: {modelo_db.model_type} v{modelo_db.model_version}")
                try:
                    buffer = BytesIO(modelo_db.model_data)
                    self.modelo = joblib.load(buffer)
                    logger.info("✅ Modelo cargado exitosamente")
                except Exception as e:
                    logger.error(f"❌ Error al cargar el modelo: {e}")
                    self.modelo = None
            else:
                logger.info("ℹ️ No se encontró modelo activo. Se usará sistema de reglas.")
                self.modelo = None

        except Exception as e:
            logger.error(f"❌ Error en _cargar_modelo: {e}")
            self.modelo = None

    def _preparar_datos_entrenamiento(self):
        """
        Prepara un DataFrame con tareas completadas del usuario para entrenar el modelo.
        Extrae características textuales y metadatos, y calcula la eficiencia real.
        """
        try:
            tareas_completadas = self.db.query(Task).filter(
                Task.user_id == self.user_id,
                Task.status == 'completed'
            ).all()

            logger.info(f"📊 Tareas completadas encontradas: {len(tareas_completadas)}")

            if len(tareas_completadas) < 2:
                logger.warning("⚠️ Menos de 2 tareas completadas. Entrenamiento no posible.")
                return None

            datos = []
            for task in tareas_completadas:
                dato = {
                    "titulo": task.title or "",
                    "descripcion": task.description or "",
                    "urgencia": task.urgency or "medium",
                    "impacto": task.impact or "medium",
                    "energia_requerida": task.energy_required or "medium",
                    "prioridad_original": task.priority_level or "medium",
                    "duracion_estimada": task.estimated_duration or 60,
                    "eficiencia": self._calcular_eficiencia(task)
                }

                # Características derivadas del texto
                dato["longitud_descripcion"] = len(dato["descripcion"])
                dato["tiene_urgente"] = 1 if "urgent" in dato["descripcion"].lower() or "crític" in dato["titulo"].lower() else 0
                dato["tiene_bug"] = 1 if "bug" in dato["titulo"].lower() or "fix" in dato["titulo"].lower() else 0

                datos.append(dato)

            return pd.DataFrame(datos) if datos else None

        except Exception as e:
            logger.error(f"❌ Error en _preparar_datos_entrenamiento: {e}")
            return None

    def _calcular_eficiencia(self, task: Task) -> float:
        """
        Calcula la eficiencia como: tiempo_estimado / tiempo_real.
        Si no hay tiempo real, usa la prioridad como proxy razonable.
        """
        try:
            feedback = self.db.query(MLFeedback).filter(
                MLFeedback.task_id == task.id,
                MLFeedback.actual_completion_time.isnot(None)
            ).first()

            if feedback and feedback.actual_completion_time and task.estimated_duration:
                eficiencia = task.estimated_duration / max(feedback.actual_completion_time, 1)
                return min(eficiencia, 3.0)  # Evitar valores extremos

            # Fallback: prioridad como indicador de importancia/eficiencia esperada
            prioridad_map = {"high": 2.0, "medium": 1.0, "low": 0.5}
            return prioridad_map.get(task.priority_level or "medium", 1.0)

        except Exception as e:
            logger.error(f"❌ Error al calcular eficiencia: {e}")
            return 1.0

    def entrenar_modelo_prioridad(self) -> bool:
        """
        Entrena un modelo SGDRegressor usando eficiencia como variable objetivo.
        Requiere al menos 2 tareas completadas.
        """
        try:
            logger.info("🎯 Iniciando entrenamiento del modelo...")
            df = self._preparar_datos_entrenamiento()
            if df is None or len(df) < 2:
                logger.warning(f"❌ Insuficientes datos para entrenar: {len(df) if df else 0}/2")
                return False

            logger.info(f"📈 Dataset preparado: {len(df)} registros")

            try:
                # Codificar variables categóricas
                df['urgencia_encoded'] = self.encoder_urgencia.fit_transform(df['urgencia'])
                df['impacto_encoded'] = self.encoder_impacto.fit_transform(df['impacto'])
                df['energia_encoded'] = self.encoder_energia.fit_transform(df['energia_requerida'])

                features = [
                    'urgencia_encoded', 'impacto_encoded', 'energia_encoded',
                    'duracion_estimada', 'longitud_descripcion',
                    'tiene_urgente', 'tiene_bug'
                ]

                X = df[features].values
                y = df['eficiencia'].values

                logger.info(f"🔢 Características: {X.shape}, Target: {y.shape}")

                # Entrenar modelo ligero y eficiente
                self.modelo = SGDRegressor(
                    max_iter=1000,
                    tol=1e-3,
                    random_state=42,
                    learning_rate='adaptive',
                    eta0=0.1
                )
                self.modelo.fit(X, y)

                logger.info("✅ Modelo entrenado exitosamente")
                self._guardar_modelo(self.modelo, "priority_predictor_v2")
                return True

            except Exception as e:
                logger.error(f"❌ Error en el proceso de entrenamiento: {e}")
                return False

        except Exception as e:
            logger.error(f"❌ Error general en entrenar_modelo_prioridad: {e}")
            traceback.print_exc()
            return False

    def _post_procesamiento(self, resultados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplica ajustes contextuales finos a los puntajes después de la predicción.
        Usa la hora actual y feedback reciente para refinar la prioridad.
        """
        try:
            hora_actual = datetime.now().hour

            # Identificar tareas con feedback negativo en las últimas 24h
            veinticuatro_horas = datetime.now() - pd.Timedelta(hours=24)
            feedbacks_negativos_recientes = self.db.query(MLFeedback).filter(
                MLFeedback.user_id == self.user_id,
                MLFeedback.created_at >= veinticuatro_horas,
                MLFeedback.was_useful == False
            ).all()
            task_ids_feedback = {f.task_id for f in feedbacks_negativos_recientes}

            for item in resultados:
                puntaje_original = item['puntaje_ml']
                task = item['task_obj']
                energia = task.energy_required or "medium"
                duracion = task.estimated_duration or 60

                ajuste = 1.0

                # Ajuste por hora del día y energía requerida
                if hora_actual >= 18:  # Tarde/noche
                    if energia == "high":
                        ajuste *= 0.7   # Penalizar alta energía
                    elif energia == "low":
                        ajuste *= 1.2   # Favorecer tareas ligeras
                elif 7 <= hora_actual <= 10:  # Mañana temprano
                    if energia == "high":
                        ajuste *= 1.15  # Ideal para tareas exigentes

                # Penalizar tareas muy largas al final del día
                if hora_actual >= 17 and duracion > 120:
                    ajuste *= 0.85

                # Impulso leve si hubo feedback negativo reciente
                # Interpretación: "el modelo subestimó esta tarea, así que aumenta su peso"
                if task.id in task_ids_feedback:
                    ajuste *= 1.1

                # Aplicar ajuste, evitando puntajes nulos
                item['puntaje_ml'] = max(puntaje_original * ajuste, 0.01)

            logger.info("⚙️ Post-procesamiento aplicado a puntajes de prioridad")
            return resultados

        except Exception as e:
            logger.error(f"❌ Error en post-procesamiento: {e}")
            return resultados  # Devuelve sin cambios si falla

    def predecir_prioridad_tareas(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Predice y ordena tareas pendientes usando ML (si está disponible) o reglas.
        Aplica post-procesamiento y devuelve lista ordenada por prioridad.
        """
        try:
            logger.info(f"🔮 Prediciendo prioridad para {len(tasks)} tareas")

            if not tasks:
                return []

            # Elegir estrategia: ML o reglas
            if self.modelo is None:
                logger.info("🤖 Modelo no disponible. Usando sistema de reglas.")
                resultados = self._prioridad_por_reglas(tasks)
            else:
                # Preparar datos para predicción
                datos_pred = []
                for task in tasks:
                    dato = {
                        'task_obj': task,
                        'urgencia': task.urgency or 'medium',
                        'impacto': task.impact or 'medium',
                        'energia_requerida': task.energy_required or 'medium',
                        'duracion_estimada': task.estimated_duration or 60,
                        'descripcion': task.description or "",
                        'titulo': task.title or ""
                    }
                    dato['longitud_descripcion'] = len(dato['descripcion'])
                    dato['tiene_urgente'] = 1 if "urgent" in dato['descripcion'].lower() or "crític" in dato['titulo'].lower() else 0
                    dato['tiene_bug'] = 1 if "bug" in dato['titulo'].lower() or "fix" in dato['titulo'].lower() else 0
                    datos_pred.append(dato)

                try:
                    # Codificar categorías usando los mismos encoders del entrenamiento
                    urgencias_encoded = self.encoder_urgencia.transform([d['urgencia'] for d in datos_pred])
                    impactos_encoded = self.encoder_impacto.transform([d['impacto'] for d in datos_pred])
                    energias_encoded = self.encoder_energia.transform([d['energia_requerida'] for d in datos_pred])

                    X_pred = np.array([
                        urgencias_encoded,
                        impactos_encoded,
                        energias_encoded,
                        [d['duracion_estimada'] for d in datos_pred],
                        [d['longitud_descripcion'] for d in datos_pred],
                        [d['tiene_urgente'] for d in datos_pred],
                        [d['tiene_bug'] for d in datos_pred]
                    ]).T

                    predicciones = self.modelo.predict(X_pred)

                    resultados = []
                    for i, dato in enumerate(datos_pred):
                        resultados.append({
                            'task_obj': dato['task_obj'],
                            'puntaje_ml': float(predicciones[i]),
                            'titulo': dato['titulo'],
                            'prioridad_original': dato['task_obj'].priority_level or "medium"
                        })

                except Exception as e:
                    logger.error(f"❌ Error en predicción con ML: {e}")
                    resultados = self._prioridad_por_reglas(tasks)

            # Aplicar post-procesamiento contextual a ambos flujos (ML y reglas)
            resultados = self._post_procesamiento(resultados)

            # Ordenar por puntaje final
            resultados_ordenados = sorted(resultados, key=lambda x: x['puntaje_ml'], reverse=True)
            logger.info(f"✅ Predicción completada para {len(resultados_ordenados)} tareas")
            return resultados_ordenados

        except Exception as e:
            logger.error(f"❌ Error en predecir_prioridad_tareas: {e}")
            # Fallback seguro
            resultados = self._prioridad_por_reglas(tasks)
            resultados = self._post_procesamiento(resultados)
            return sorted(resultados, key=lambda x: x['puntaje_ml'], reverse=True)

    def _prioridad_por_reglas(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Sistema de respaldo basado en reglas heurísticas.
        Se usa cuando no hay modelo entrenado.
        """
        logger.info("📋 Usando sistema de reglas para priorización")

        prioridad_map = {"high": 3, "medium": 2, "low": 1}
        urgencia_map = {"high": 1.5, "medium": 1.2, "low": 1.0}
        impacto_map = {"high": 1.3, "medium": 1.1, "low": 1.0}

        resultados = []
        for task in tasks:
            puntaje_base = prioridad_map.get(task.priority_level or "medium", 1)

            # Ajuste por palabras clave en título o descripción
            descripcion = (task.description or "").lower()
            titulo = (task.title or "").lower()

            if any(word in titulo for word in ['bug', 'fix', 'crític', 'urgent', 'hotfix']):
                puntaje_base *= 1.8
            elif any(word in descripcion for word in ['urgent', 'important', 'critical']):
                puntaje_base *= 1.4

            # Ajuste por metadatos
            puntaje_base *= urgencia_map.get(task.urgency or "medium", 1.0)
            puntaje_base *= impacto_map.get(task.impact or "medium", 1.0)

            # Ajuste por deadline cercano
            if task.deadline:
                dias_restantes = (task.deadline - datetime.now()).days
                if dias_restantes <= 0:
                    puntaje_base *= 2.5
                elif dias_restantes <= 1:
                    puntaje_base *= 2.0
                elif dias_restantes <= 3:
                    puntaje_base *= 1.5

            resultados.append({
                'task_obj': task,
                'puntaje_ml': float(puntaje_base),
                'titulo': task.title,
                'prioridad_original': task.priority_level or "medium"
            })

        return resultados

    def _guardar_modelo(self, modelo, model_type: str = "priority_predictor"):
        """Guarda el modelo serializado en la tabla AIModel."""
        try:
            # Desactivar versiones anteriores
            self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.model_type == model_type
            ).update({"is_active": False})

            buffer = BytesIO()
            joblib.dump(modelo, buffer)
            modelo_bin = buffer.getvalue()

            nuevo_modelo = AIModel(
                user_id=self.user_id,
                model_type=model_type,
                model_version="2.0",
                model_data=modelo_bin,
                feature_weights={},
                accuracy_metrics={"trained_at": datetime.now().isoformat()},
                is_active=True
            )

            self.db.add(nuevo_modelo)
            self.db.commit()
            logger.info("💾 Modelo guardado en base de datos")

        except Exception as e:
            logger.error(f"❌ Error al guardar el modelo: {e}")
            self.db.rollback()

    def recomendar_horario(self, task: Task) -> str:
        """
        Recomienda una hora del día basada en la energía requerida y el tipo de tarea.
        """
        try:
            hora_recomendada = "10:00"

            energia = task.energy_required or "medium"
            titulo = (task.title or "").lower()

            if energia == "high" or any(word in titulo for word in ['bug', 'fix', 'critical']):
                hora_recomendada = "08:00"   # Mañana temprano
            elif energia == "medium":
                hora_recomendada = "14:00"   # Tarde
            else:
                hora_recomendada = "16:00"   # Final del día

            logger.info(f"⏰ Horario recomendado para '{task.title}': {hora_recomendada}")
            return hora_recomendada

        except Exception as e:
            logger.error(f"❌ Error en recomendar_horario: {e}")
            return "10:00"