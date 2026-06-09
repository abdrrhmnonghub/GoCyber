from django.apps import AppConfig


from django.apps import AppConfig
import joblib
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    # Siapkan tempat untuk pipeline dan akurasi
    ml_pipeline = None
    model_accuracy = 0

    def ready(self):
        model_path = os.path.join(os.path.dirname(__file__), 'rf_pipeline.joblib')
        try:
            # Load file joblib
            saved_data = joblib.load(model_path)
            
            # Ekstrak pipeline dan akurasinya
            self.ml_pipeline = saved_data['pipeline']
            self.model_accuracy = saved_data['accuracy']
            print("=====[ MACHINE LEARNING PIPELINE LOADED ]=====")
        except Exception as e:
            print(f"=====[ ERROR LOADING PIPELINE: {e} ]=====")