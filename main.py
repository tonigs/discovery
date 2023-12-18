from flask import Flask, render_template, jsonify, request
import subprocess
import json

app = Flask(__name__)


def get_srt_info():
    try:
        result = subprocess.run(
            ["ffprobe", "-show_streams", "-print_format", "json", "-timeout", "4000000", "-i",
             "srt://localhost:1227?mode=listener"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error executing ffprobe: {result.stderr}"

    except Exception as e:
        return f"Error executing ffprobe: {e}"


@app.route('/')
def index():
    return render_template('in.html')


@app.route('/get_streams')
def get_streams():
    streams_info = get_srt_info()
    #print(streams_info)

    if streams_info is not None:
        return streams_info
    else:
        return "Error al obtener información de streams."


@app.route('/display_streams')
def display_streams():
    streams_info = get_srt_info()
    #print(streams_info)
    if streams_info is not None:
        # Ordenar la lista de streams por algún criterio si es necesario

        return render_template('display_streams.html', streams_info=json.loads(streams_info))
    else:
        return "No se encontraron streams."





# Nueva ruta para retranscodificar el stream
@app.route('/retranscode', methods=['POST'])
def retranscode():
    # Obtener la información enviada desde el cliente
    data = request.get_json()
    print(data)
    languages = []
    i = 0
    for field_dict in data:

        if field_dict['type'] == 'audio':
            md_key = f"-metadata:s:a:{i}"
            md_value = f"language={field_dict['tags.language']}"
            languages.extend([md_key, md_value])
            i += 1

    #print(languages)

        if field_dict['type'] == 'video':
            #vd_key_map = f"-c:v:{v}"
            vd_codec = f"{field_dict['codec_name']}"
            vd_key_br = f""



    try:
        result = subprocess.run(
            ["ffmpeg", "-i", "srt://localhost:1227?mode=listener"] + languages + ["-c:v", "copy", "-c:a", "copy", "-map", "0",
              "-f", "MPEGTS","srt://localhost:1478"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error executing transcoding: {result.stderr}"

    except Exception as e:
        return f"Error executing transcoding: {e}"
    # Aquí deberías incluir la lógica para retranscodificar el stream usando ffmpeg
    # Puedes acceder a la información utilizando data['streams']
    # Ejemplo:
    #for stream in data['streams']:
        # Lógica de retranscodificación para el stream actual
        # ...

    # Devolver una respuesta (puedes ajustar según necesites)
    return jsonify({'status': 'success'})







if __name__ == "__main__":
    app.run(debug=True)