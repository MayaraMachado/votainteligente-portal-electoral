# coding=utf-8
from collections import OrderedDict

WHEN_CHOICES = [
    ('', u'¿Cuándo?'),
    ('1_year', u'1 año'),
    ('2_year', u'2 años'),
    ('3_year', u'3 años'),
    ('4_year', u'4 años'),
]

TOPIC_CHOICES = (('', u'Selecciona una categoría'),
                 ('asistencia', u'Asistencia y protección social'),
                 ('ciencias', u'Ciencias'),
                 ('cultura', u'Cultura'),
                 ('deporte', u'Deporte'),
                 ('derechoshumanos', u'Derechos Humanos'),
                 ('derechos', u'Derechos Sociales'),
                 ('emergencia', u'Desastres Naturales'),
                 ('economia', u'Economía'),
                 ('educacion', u'Educación'),
                 ('empleo', u'Empleo'),
                 ('energia', u'Energía'),
                 ('genero', u'Equidad y género'),
                 ('diversidad', u'Inclusión'),
                 ('infancia', u'Infancia y juventud'),
                 ('justicia', u'Justicia'),
                 ('medioambiente', u'Medio ambiente'),
                 ('medios', u'Medios de comunicación'),
                 ('migracion', u'Migración'),
                 ('mineria', u'Minería'),
                 ('pensiones', u'Pensiones'),
                 ('participacion', u'Participación'),
                 ('prevision', u'Previsión'),
                 ('proteccionsocial', u'Protección social'),
                 ('pueblosoriginarios', u'Pueblos originarios'),
                 ('recursosnaturales', u'Recursos naturales'),
                 ('salud', u'Salud'),
                 ('seguridad', u'Seguridad'),
                 ('sustentabilida', u'Sustentabilidad'),
                 ('terceraedad', u'Tercera Edad'),
                 ('trabajo', u'Trabajo'),
                 ('transparencia', u'Transparencia'),
                 ('transporte', u'Transporte'),
                 ('espaciospublicos', u'Urbanismo y Espacios públicos'),
                 )

TEXTS = OrderedDict({
    'problem': {'label': u'¿Cuál es el problema?',
                'preview_question': u'¿Cuál es el problema que quieres solucionar?',
                'help_text': u'',
                'placeholder': u'Escribe el problema que quieres solucionar con tu propuesta.',
                'long_text': "paso1.html"},
    'causes': {'label': u'¿Por qué existe el problema?',
               'preview_question': u'Cuáles son las causas de este problema?',
               'help_text': u'',
               'placeholder': u'Escribe aquí la causa de tu problema que quieres abordar. Recuerda solo escribir una.',
               'long_text': "paso2.html"},
    'solution': {'label': u'¿Cuáles posibles soluciones creemos que existen para pasar del problema a la situación ideal?',
                 'preview_question': u'¿Cual sería la situación ideal?',
                 'help_text': u'',
                 'placeholder': u'Escribe aquí la situación ideal a la que quieres llegar.',
                 'long_text': "paso3.html"},
    'solution_at_the_end': {'label': u'¿Qué acción dará por cumplida la tarea del alcalde?',
                            'preview_question': u'¿Cuál sería la solución?',
                            'help_text': u'',
                            'placeholder': u'Escribe aquí la solucion para el problema que definiste.',
                            'long_text': "paso4a.html"},
    'when': {'label': u'¿Cuándo?',
             'preview_question': u'¿Cuándo debería estar esto listo?',
             'help_text': u'1_year',
             'placeholder': u'',
             'long_text': "paso4b.html"},
    'title': {'label': u'Colócale título',
              'preview_question': u'Título',
              'help_text': u'',
              'placeholder': u'Título de la propuesta',
              'long_text': "paso5a.html"},
    'join_advocacy_url': {'label': u'Link a tu grupo en WhatsApp',
              'preview_question': u'http://wsp.com/migrupo',
              'help_text': u'http://wsp.com/migrupo',
              'placeholder': u'http://wsp.com/migrupo',
              'long_text': "paso5b.html"},
    'clasification': {'label': u'Primero elige una categoría',
                      'preview_question': u'Clasificación',
                      'help_text': u'educacion',
                      'placeholder': u'',
                      'long_text': "paso5b.html"},
    'is_local_gathering': {'label': u'¿Esta propuesta es producto de un encuentro local?',
                      'preview_question': u'¿Es un encuentro local?',
                      'help_text': u'',
                      'placeholder': u'',
                      'long_text': ""},
    'terms_and_conditions': {'label': u'Términos y condiciones',
                             'preview_question': u'',
                             'help_text': u'',
                             'placeholder': u'',
                             'long_text': "terms_and_conditions.html"},
    'is_testing': {'label': u'Esta propuesta es de prueba',
                             'preview_question': u'',
                             'help_text': u'Sólo la podrás ver tu y nosotros podremos borrarlas periodicamente.',
                             'placeholder': u'',
                             'long_text': "paso5b.html"},
})
