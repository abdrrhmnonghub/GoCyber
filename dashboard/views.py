from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
import json
def home(request):
    # Render tampilan terminal
    return render(request, 'dashboard/base.html')

def validasi_key(request):
    if request.method == 'POST':
        try:
            # Membaca data JSON yang dikirim oleh Javascript
            data = json.loads(request.body)
            input_key = data.get('key')
            
            if input_key == "admin123":
                # Jika benar, beri "tiket masuk" berupa session
                request.session['is_auth'] = True
                request.session.set_expiry(120) # Berlaku 1 jam
                return JsonResponse({'status': 'success', 'message': 'Access Granted. Module Unlocked.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Access Denied: Invalid Security Key.'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Bad Request'})
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

from django.shortcuts import render, redirect
from django.apps import apps
import pandas as pd

def predict(request):
    if not request.session.get('is_auth'):
        return redirect('access_denied')

    context = {}
    if request.method == 'POST':
        try:
            # Tangkap 8 parameter dari Form HTML
            enkripsi = request.POST.get('encryption_used')
            browser = request.POST.get('browser_type')
            protokol = request.POST.get('protocol_type')
            
            login = int(request.POST.get('login_attempts', 0))
            login_failed = int(request.POST.get('failed_logins', 0))
            waktu_sesi = float(request.POST.get('session_duration', 0.0))
            paket = int(request.POST.get('network_packet_size', 0))
            ip_reputation = float(request.POST.get('ip_reputation_score', 0.0))

            # Susun menjadi Pandas DataFrame (nama kolom WAJIB sama persis dengan di Colab)
            input_data = pd.DataFrame([[
                enkripsi, browser, protokol, login, 
                login_failed, waktu_sesi, paket, ip_reputation
            ]], columns=[
                'encryption_used', 'browser_type', 'protocol_type', 'login_attempts',
                'failed_logins', 'session_duration', 'network_packet_size', 'ip_reputation_score'
            ])

            # Panggil pipeline dari apps.py
            model_config = apps.get_app_config('dashboard')
            pipeline = model_config.ml_pipeline
            akurasi_training = model_config.model_accuracy

            if pipeline:
                # Lakukan Prediksi (Ambil Probabilitas)
                probs = pipeline.predict_proba(input_data)[0]
                pred_label = probs.argmax()
                
                # Dictionary Pemetaan Serangan
                attack_mapping = {
                    0: "Brute force",
                    1: "Malware",
                    2: "Normal",
                    3: "Suspicious"
                }
                
                hasil = attack_mapping.get(pred_label, "Unknown")
                confidence = round(probs[pred_label] * 100, 2)

                context = {
                    'status': f'SUCCESS ({confidence}%)',
                    'hasil_prediksi': f'Deteksi: {hasil}',
                    'info_tambahan': f'Akurasi Dasar Model: {round(akurasi_training * 100, 2)}%',
                    'parameter_masuk': [enkripsi, browser, protokol, login, login_failed, waktu_sesi, paket, ip_reputation]
                }

        except Exception as e:
            context = {
                'status': 'ERROR',
                'hasil_prediksi': f'Gagal memproses data: {str(e)}'
            }
            
    return render(request, 'dashboard/predict.html', context)
# FUNGSI BARU: Render halaman penolakan
def access_denied(request):
    return render(request, 'dashboard/access_denied.html')

def error_404(request, exception):
    # Merender halaman 404 kustom dengan status code HTTP 404
    return render(request, 'dashboard/error_404.html', status=404)