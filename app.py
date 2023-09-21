from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from PIL import Image
import binascii
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def encode(x):
    return binascii.hexlify(x.encode('utf-8')).decode()

def decode(x):
    return binascii.unhexlify(x.encode('utf-8')).decode()


@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        apply_mask(filename)
        os.remove(filename)

        return redirect(url_for('image_gallery'))

@app.route('/gallery')
def image_gallery():
    image_folder = 'static/images'
    allowed_extensions = {'jpg', 'jpeg', 'png'}  # Extensões permitidas

    # Filtrar os arquivos na pasta "images" por extensão permitida
    image_files = [f for f in os.listdir(image_folder) if f.split('.')[-1].lower() in allowed_extensions]

    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(image_folder, x)), reverse=True)

    return render_template('gallery.html', image_files=image_files)


def apply_mask(filename):
    input_image = Image.open(filename).convert('RGBA')
    mask = Image.open('assets/mask.png').convert('RGBA')

    # Redimensionar a imagem de entrada para ter o mesmo tamanho da máscara
    mask = mask.resize(input_image.size)

    # Aplicar a máscara à imagem de entrada
    result_image = Image.new('RGBA', input_image.size)
    result_image.paste(input_image, (0, 0))
    result_image.paste(mask, (0, 0), mask)

    # Converter a imagem resultante para o modo RGB antes de salvar em JPEG
    result_image = result_image.convert('RGB')

    # Obter a data e hora atual no formato yyyyMMdd_HHmmss
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Concatenar o prefixo "adidas_" com a data e hora
    result_filename = f'static/images/adidas_{current_datetime}.jpg'

    result_image.save(result_filename, 'JPEG')

if __name__ == '__main__':
    app.run(debug=True)
