import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from matplotlib.widgets import Slider
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Button

#базова функція, яка приймає всі потрібні значення
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    time = np.linspace(0, 10, 1000) #гененрація значень, які будуть використані в осі часу

    harmony = amplitude * np.sin((2 * np.pi * frequency * time) + phase) #визначення виду функції гармоніки

    np.random.seed(42) 
    noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(time)) #генерація значень шуму
    
    if show_noise: #тут ініціалізація перевірки прапорця "показувати шум"
        final_signal = harmony + noise
    else:
        final_signal = harmony 
        
    return final_signal, harmony, time

#це просто виклик базової функції зі значеннями всіх атрибутів 
noisy_signal, pure_signal, t = harmonic_with_noise(
    amplitude=0.97, 
    frequency=0.267, 
    phase=0.0, 
    noise_mean=0.108, 
    noise_covariance=0.101, 
    show_noise=True
)

#тут ініціалізація фігури графіка 
fig, ax = plt.subplots(figsize=(10, 6))
fig.subplots_adjust(bottom=0.45)

fs = 1000 / 10 #частота дисркетизації
b, a = butter(3, 2.0, fs=fs, btype='low') #створюю "фільтр" для шуму
filtered_signal = filtfilt(b, a, noisy_signal) #застосовую фільтр до сигналу з шумом

#тут малюються лінії, при цьому вони присвоюються змінним, щоб далі ними оперувати 
line_pure, = ax.plot(t, pure_signal, label="clean signal", color='blue', linewidth=4)
line_noisy, = ax.plot(t, noisy_signal, label="noisy signal", color='green', linewidth=2, alpha=0.7)
line_filtered, = ax.plot(t, filtered_signal, label="filtered signal", color='orange', linewidth=4, linestyle='--')

#налаштовую слайдери
ax_cutoff = plt.axes([0.2, 0.35, 0.6, 0.03])
ax_noise_cov = plt.axes([0.2, 0.30, 0.6, 0.03])
ax_noise_mean = plt.axes([0.2, 0.25, 0.6, 0.03])
ax_phase = plt.axes([0.2, 0.20, 0.6, 0.03])
ax_freq = plt.axes([0.2, 0.15, 0.6, 0.03])
ax_amp = plt.axes([0.2, 0.10, 0.6, 0.03])
slider_cutoff = Slider(ax_cutoff, 'cutoff freq', 0.1, 10.0, valinit=5.0)
slider_noise_cov = Slider(ax_noise_cov, 'noise cov', 0.0, 1.0, valinit=0.101)
slider_noise_mean = Slider(ax_noise_mean, 'noise mean', -1.0, 1.0, valinit=0.108)
slider_phase = Slider(ax_phase, 'phase', 0.0, 2*np.pi, valinit=0.0)
slider_freq = Slider(ax_freq, 'frequency', 0.1, 2.0, valinit=0.267)
amp_slider = Slider(ax_amp, 'amplitude', 0.1, 5.0, valinit=0.97)

#налаштовую кнопки
ax_noiseavailable = plt.axes([0.8, 0.05, 0.15, 0.08])
noiseavailable = CheckButtons(ax_noiseavailable, ['show noise'], [True])
status = noiseavailable.get_status()[0]

ax_reset = plt.axes([0.05, 0.05, 0.1, 0.05])
btn_reset = Button(ax_reset, 'reset')

#тут функція для апдейту значень відповідно до руху повзунків/натискання кнопки
def update(val):
    current_amp = amp_slider.val
    current_freq = slider_freq.val
    current_phase = slider_phase.val
    current_noise_mean = slider_noise_mean.val
    current_noise_cov = slider_noise_cov.val
    current_cutoff = slider_cutoff.val
    is_on = noiseavailable.get_status()[0]

    #перераховуємо все відповідно до нових значень
    new_noisy, new_pure, _ = harmonic_with_noise(
        amplitude=current_amp, 
        frequency=current_freq, 
        phase=current_phase, 
        noise_mean=current_noise_mean, 
        noise_covariance=current_noise_cov, 
        show_noise=is_on
    )
    
    #оновлюємо фільтр
    b, a = butter(3, current_cutoff, fs=fs, btype='low')
    new_filtered = filtfilt(b, a, new_noisy)

    #записуємо нові дані в лінії
    line_pure.set_ydata(new_pure)
    line_noisy.set_ydata(new_noisy)
    line_filtered.set_ydata(new_filtered)

    fig.canvas.draw_idle()

amp_slider.on_changed(update)
slider_freq.on_changed(update)
slider_phase.on_changed(update)
slider_noise_mean.on_changed(update)
slider_noise_cov.on_changed(update)
slider_cutoff.on_changed(update)
noiseavailable.on_clicked(update)

#функція для ресету всіх значень
def reset(event):
    amp_slider.reset()
    slider_freq.reset()
    slider_phase.reset()
    slider_noise_mean.reset()
    slider_noise_cov.reset()
    slider_cutoff.reset()

btn_reset.on_clicked(reset)
    
ax.legend() 
plt.show()

