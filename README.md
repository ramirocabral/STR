<div align="center">
  <img 
    src="https://github.com/user-attachments/assets/40ba8ff4-5c20-4c61-be82-7024bcd1efb2"
    alt="ElectricSim Logo"
    width="100%"
  >
</div>

# Proyecto G8: ElectricSim – Plataforma de simulación y predicción de demanda eléctrica

## Descripción del proyecto

**ElectricSim** es una plataforma educativa orientada al análisis, simulación y predicción de la **demanda eléctrica en el Gran Buenos Aires (GBA)**. El sistema integra **fuentes de datos energéticas, meteorológicas y astronómicas**, las consolida mediante **Apache Kafka** y las expone a un **modelo de deep learning** capaz de anticipar variaciones en el consumo eléctrico y detectar comportamientos anómalos en tiempo real.

El proyecto busca servir como entorno experimental para el estudio de **sistemas distribuidos**, **procesamiento de datos en streaming** y **machine learning aplicado al dominio energético**, combinando datos históricos y datos en tiempo real dentro de una arquitectura desacoplada y escalable.

<details>
  <summary><i>Características del proyecto</i></summary>
  <ol>
    <li><b>Integración de múltiples fuentes de datos</b></li>
    <p>El sistema unifica información energética oficial, datos meteorológicos y variables astronómicas relevantes para el modelado del consumo eléctrico.</p>

  <li><b>Procesamiento de datos en tiempo real</b></li>
  <p>Los datos actuales son distribuidos mediante Apache Kafka, permitiendo desacoplar la recolección de datos del procesamiento analítico.</p>

  <li><b>Modelo predictivo basado en deep learning</b></li>
  <p>Una red neuronal feedforward permite estimar la demanda eléctrica a partir de variables climáticas, temporales y energéticas.</p>

  <li><b>Inferencia bajo demanda</b></li>
  <p>El sistema expone una API REST que permite realizar predicciones puntuales y simulaciones con datos de pronóstico.</p>

  <li><b>Detección de anomalías en tiempo real</b></li>
  <p>Se detectan desvíos significativos entre valores reales y predichos mediante Server-Sent Events (SSE).</p>
  </ol>
</details>

<details>
  <summary><i>Beneficios</i></summary>
  <ol>
    <li>Anticipación de picos de consumo</li>
    <p>Permite prever aumentos o caídas en la demanda eléctrica con antelación.</p>

  <li>Análisis energético integral</li>
  <p>Combina variables ambientales, temporales y operativas en un único modelo.</p>

  <li>Arquitectura escalable</li>
  <p>El uso de Kafka permite escalar productores y consumidores de datos de forma independiente.</p>

  <li>Aplicación educativa</li>
  <p>Sirve como base para el estudio de sistemas distribuidos y machine learning aplicado.</p>
  </ol>
</details>

<details>
  <summary><i>Tecnologías utilizadas</i></summary>
  <ol>

  <li>Fuentes de datos</li>
  <ul>
    <li>CAMMESA API: datos oficiales de generación y demanda eléctrica</li>
    <li>OpenWeather API: variables meteorológicas</li>
    <li>Sunrise-Sunset API: información astronómica</li>
  </ul>

  <li>Streaming y mensajería</li>
  <ul>
    <li>Apache Kafka</li>
    <li>Kafka Streams</li>
  </ul>

  <li>Backend y procesamiento</li>
  <ul>
    <li>Spring Boot: recolección y exposición de datos</li>
    <li>Python + FastAPI: inferencia, detección de anomalías y SSE</li>
    <li>APIs HTTP/REST</li>
    <li>Server-Sent Events (SSE)</li>
  </ul>

  <li>Machine Learning</li>
  <ul>
    <li>TensorFlow / Keras</li>
    <li>Scikit-learn</li>
    <li>Pandas y NumPy</li>
  </ul>

  <li>Infraestructura</li>
  <ul>
    <li>Docker</li>
    <li>Docker Compose</li>
  </ul>

  </ol>
</details>

---

<h1 id="architecture">Arquitectura del sistema</h1>

<p>ElectricSim se organiza en dos bloques funcionales principales:</p>

<img width="100%" alt="esquema_completo" src="https://github.com/user-attachments/assets/2118839a-ce69-4528-8362-0c713d75b9a6" />

<ul>
  <li><b>Recolección y distribución de datos:</b> las fuentes energéticas, meteorológicas y astronómicas son consultadas de manera periódica por un backend desarrollado en Spring Boot. En este proceso, solo los datos en tiempo real son enviados hacia Apache Kafka, que actúa como sistema de mensajería y desacople entre productores y consumidores. Por otro lado, los datos históricos no pasan por Kafka: quedan disponibles directamente a través de un endpoint específico del backend, desde donde luego son consumidos para el proceso de entrenamiento del modelo. Paralelamente, los datos en tiempo real almacenados en Kafka se utilizan para la visualización continua mediante Grafana. </li>
  <li><b>Entrenamiento del modelo:</b> los datos provenientes de Kafka (en tiempo real) y los datos históricos previamente almacenados son procesados mediante un módulo de preprocesamiento que limpia, transforma y organiza la información. Luego, estos datos alimentan un modelo de deep learning diseñado para predecir la demanda eléctrica. Una vez entrenado, el modelo se expone mediante una API que no solo permite realizar inferencias, sino que también ofrece un endpoint para la obtención de anomalías cada 5 minutos mediante SSE. Además, este bloque integra datos en tiempo real para reentrenar periódicamente el modelo con información más reciente, permitiendo que la red se adapte a los cambios actuales del sistema.</li>



</ul>

---

<h1 id="structure">Estructura del proyecto</h1>

<p>
Este repositorio corresponde exclusivamente al <b>módulo de Deep Learning de ElectricSim</b>.
Aquí se implementa el modelo predictivo, el preprocesamiento de datos, la inferencia,
la detección de anomalías y el mecanismo de reentrenamiento en tiempo real.
</p>

<p>
La recolección de datos, la publicación en Kafka y la visualización del sistema forman parte
de otros repositorios del proyecto ElectricSim y <b>no se encuentran incluidos aquí</b>.
</p>

<pre>
ElectricSim-ML/
│
├── api/                    # API de inferencia y streaming (FastAPI, SSE)
├── data/                   # Datos utilizados para entrenamiento y reentrenamiento
├── lib/                    # Utilidades de preprocesamiento y helpers
├── ml/                     # Lógica principal de entrenamiento y reentrenamiento
├── models/                 # Modelos entrenados y escaladores (StandardScaler)
│
├── model.ipynb             # Notebook experimental de diseño y evaluación del modelo
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación del módulo
├── LICENSE                 # Licencia del proyecto
├── __init__.py
└── __pycache__/            # Archivos de cache de Python
</pre>

---

<h1 id="scope">Alcance del repositorio</h1>

<p>
Este repositorio contiene <b>únicamente la implementación del modelo de Deep Learning</b>
utilizado por ElectricSim.
</p>

<ul>
  <li>Preprocesamiento de datos energéticos, climáticos y temporales</li>
  <li>Entrenamiento inicial del modelo predictivo</li>
  <li>Inferencia bajo demanda mediante API REST</li>
  <li>Detección de anomalías en tiempo real mediante Server-Sent Events (SSE)</li>
  <li>Reentrenamiento automático e incremental del modelo</li>
</ul>

<p>
La arquitectura completa de ElectricSim incluye otros componentes como la recolección
de datos desde APIs externas, la publicación en Apache Kafka y la visualización del sistema,
los cuales se desarrollan y despliegan en repositorios independientes.
</p>

---

<h1 id="flow">Flujo de funcionamiento del sistema</h1>

<details>
  <summary><i>Flujo general de ElectricSim</i></summary>
  <ol>
    <li><b>Recolección de datos</b></li>
    <p>El backend consulta periódicamente las APIs de CAMMESA, OpenWeather y Sunrise-Sunset.</p>

  <li><b>Publicación en Kafka</b></li>
  <p>Los datos en tiempo real se publican en tópicos de Apache Kafka.</p>

  <li><b>Consumo y preprocesamiento</b></li>
  <p>El backend analítico consume los datos, los limpia y los transforma.</p>

  <li><b>Inferencia del modelo</b></li>
  <p>El modelo de deep learning predice la demanda eléctrica.</p>

  <li><b>Detección de anomalías</b></li>
  <p>Se comparan valores reales y predichos y se notifican desvíos mediante SSE.</p>

  <li><b>Reentrenamiento periódico</b></li>
  <p>El modelo se reentrena automáticamente con datos recientes.</p>
  </ol>
</details>

---

<h1 id="startup">Puesta en marcha del sistema</h1>

<p>
ElectricSim utiliza <b>Docker</b> y <b>Docker Compose</b> para simplificar la ejecución del entorno completo de desarrollo.
</p>

<p>Para construir las imágenes y levantar los servicios:</p>

```bash
docker compose up --build
```

<p>Para detener el entorno y liberar los recursos:</p>

```bash
docker compose down
```

<h1 id="authors">Autores</h1>

<ul>
  <li>
    <a href="https://www.linkedin.com/in/gonblas/">
      <img align="right" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
    </a>
    <a href="https://github.com/gonblas">
      <img align="right" src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" style="margin-right: 5px;" />
    </a>
    <strong>Blasco, Gonzalo</strong>
    <br clear="right"/>
  </li>

  <li>
    <a href="https://www.linkedin.com/in/ramirocabral04/">
      <img align="right" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
    </a>
    <a href="https://github.com/ramirocabral">
      <img align="right" src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" style="margin-right: 5px;" />
    </a>
    <strong>Cabral, Ramiro Nicolás</strong>
    <br clear="right"/>
  </li>

  <li>
    <a href="https://www.linkedin.com/in/manuel-savenia-b38639363/">
      <img align="right" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
    </a>
    <a href="https://github.com/manuSavenia">
      <img align="right" src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" style="margin-right: 5px;" />
    </a>
    <strong>Savenia, Manuel</strong>
    <br clear="right"/>
  </li>
</ul>
