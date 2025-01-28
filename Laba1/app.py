from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, DecimalField
from wtforms.validators import DataRequired
from flask_wtf.recaptcha import RecaptchaField
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '6Lcz0cQqAAAAAL6w656PF3R0kZDJo6MxGwEpND1n'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Настройка ключей reCAPTCHA
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lcz0cQqAAAAACr4eHYZStrZzvXYXja3HyYVGIeE'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lcz0cQqAAAAAL6w656PF3R0kZDJo6MxGwEpND1n'

class UploadForm(FlaskForm):
    file = FileField('Файл изображения', validators=[DataRequired()])
    contrast_level = DecimalField('Уровень контрастности (1,0 = без изменений)', default=1.0, validators=[DataRequired()])
    recaptcha = RecaptchaField()  # Добавление поля reCAPTCHA
    submit = SubmitField('Показать результат')

@app.route('/', methods=['GET', 'POST'])
 # Функция обработки изображения и проверки капчи
def index():
    form = UploadForm()
    # Проверка успешной прохождения reCAPTCHA
    if form.validate_on_submit():
            file = form.file.data
            contrast_level = form.contrast_level.data

            if file:
                filename = file.filename

                # Создание пути для сохранения изображения
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Обработка изображения
                img = Image.open(file_path)
                enhancer = ImageEnhance.Contrast(img)
                img_enhanced = enhancer.enhance(contrast_level)

                # Сохранение обработанного изображения
                enhanced_path = os.path.join(app.config['UPLOAD_FOLDER'], f'enhanced_{filename}')
                img_enhanced.save(enhanced_path)

                plot_color_distribution(img, enhanced_path)

                return render_template('result.html', original_image=file_path, enhanced_image=enhanced_path)

    # Если капча не прошла, добавляем сообщение об ошибке
    if form.recaptcha.errors:
        form.recaptcha.errors.append('Необходимо пройти проверку reCAPTCHA')

    return render_template('index.html', form=form)

# Функция построения графиков распредления цветов
def plot_color_distribution(original_img, enhanced_img_path):
    # Плотность цветовых распределений
    original_img_np = np.array(original_img)
    enhanced_img_np = np.array(Image.open(enhanced_img_path))

    plt.figure(figsize=(12, 6))

    # График для оригинального изображения
    plt.subplot(1, 2, 1)
    plt.hist(original_img_np.ravel(), bins=256, color='red', alpha=0.5, label='Красный канал')
    plt.hist(original_img_np[..., 1].ravel(), bins=256, color='green', alpha=0.5, label='Зеленый канал')
    plt.hist(original_img_np[..., 2].ravel(), bins=256, color='blue', alpha=0.5, label='Синий канал')
    plt.title('Распределение цветов исходного изображения')
    plt.xlabel('Значение интенсивности')   
    plt.ylabel('Количество пикселей')
    plt.legend(loc='upper right')

    # График для обработанного изображения
    plt.subplot(1, 2, 2)
    plt.hist(enhanced_img_np.ravel(), bins=256, color='red', alpha=0.5, label='Красный канал')
    plt.hist(enhanced_img_np[..., 1].ravel(), bins=256, color='green', alpha=0.5, label='Зеленый канал')
    plt.hist(enhanced_img_np[..., 2].ravel(), bins=256, color='blue', alpha=0.5, label='Синий канал')
    plt.title('Обработанное распределение цветов изображения')
    plt.xlabel('Значение интенсивности')
    plt.ylabel('Количество пикселей')
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'color_distribution.png'))
    plt.close()

@app.route('/result/<path:image_name>')
def result(image_name):
    return render_template('result.html', image_name=image_name)

if __name__ == '__main__':
    app.run(debug=True)
