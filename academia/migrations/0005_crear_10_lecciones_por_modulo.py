from django.db import migrations


CATALOGO = {
    'Vocales': [
        ('Conociendo la A', 'A', '🐝', 'Escucha el sonido de la A. Observa la letra y trázala.'),
        ('Conociendo la E', 'E', '🐘', 'Escucha el sonido de la E. Observa la letra y trázala.'),
        ('Conociendo la I', 'I', '🦎', 'Escucha el sonido de la I. Observa la letra y trázala.'),
        ('Conociendo la O', 'O', '🐻', 'Escucha el sonido de la O. Observa la letra y trázala.'),
        ('Conociendo la U', 'U', '🍇', 'Escucha el sonido de la U. Observa la letra y trázala.'),
        ('La vocal A en palabras', 'A', '🌳', 'Escucha la vocal A en la palabra árbol. Traza la A.'),
        ('La vocal E en palabras', 'E', '⭐', 'Escucha la vocal E en la palabra estrella. Traza la E.'),
        ('La vocal I en palabras', 'I', '🏝️', 'Escucha la vocal I en la palabra isla. Traza la I.'),
        ('La vocal O en palabras', 'O', '🐻', 'Escucha la vocal O en la palabra oso. Traza la O.'),
        ('Repaso de las cinco vocales', 'AEIOU', '🔤', 'Escucha las cinco vocales y traza cada una en orden.'),
    ],
    'Sílabas': [
        ('Sílabas con M', 'MA', '🖐️', 'Escucha y traza la sílaba MA.'),
        ('Sílabas con P', 'PE', '⚽', 'Escucha y traza la sílaba PE.'),
        ('Sílabas con S', 'SI', '☀️', 'Escucha y traza la sílaba SI.'),
        ('Sílabas con L', 'LO', '🌙', 'Escucha y traza la sílaba LO.'),
        ('Sílabas con T', 'TA', '🐢', 'Escucha y traza la sílaba TA.'),
        ('Sílabas con N', 'NO', '☁️', 'Escucha y traza la sílaba NO.'),
        ('Sílabas con C', 'CA', '🏠', 'Escucha y traza la sílaba CA.'),
        ('Sílabas con B', 'BO', '🚤', 'Escucha y traza la sílaba BO.'),
        ('Sílabas con R', 'RA', '🐸', 'Escucha y traza la sílaba RA.'),
        ('Formamos una palabra', 'MESA', '🪑', 'Escucha la palabra mesa. Observa cada letra y traza la palabra.'),
    ],
    'Trazo': [
        ('Traza la A', 'A', '✍️', 'Sigue la forma de la letra A con tu dedo o el ratón.'),
        ('Traza la E', 'E', '✍️', 'Sigue la forma de la letra E con tu dedo o el ratón.'),
        ('Traza la I', 'I', '✍️', 'Sigue la forma de la letra I con tu dedo o el ratón.'),
        ('Traza la O', 'O', '✍️', 'Sigue la forma de la letra O con tu dedo o el ratón.'),
        ('Traza la U', 'U', '✍️', 'Sigue la forma de la letra U con tu dedo o el ratón.'),
        ('Traza la M', 'M', '✍️', 'Sigue la forma de la letra M con tu dedo o el ratón.'),
        ('Traza la P', 'P', '✍️', 'Sigue la forma de la letra P con tu dedo o el ratón.'),
        ('Traza la S', 'S', '✍️', 'Sigue la forma de la letra S con tu dedo o el ratón.'),
        ('Traza la R', 'R', '✍️', 'Sigue la forma de la letra R con tu dedo o el ratón.'),
        ('Traza la L', 'L', '✍️', 'Sigue la forma de la letra L con tu dedo o el ratón.'),
    ],
    'Números': [
        ('Conociendo el número 1', '1', '☝️', 'Escucha y traza el número uno.'),
        ('Conociendo el número 2', '2', '✌️', 'Escucha y traza el número dos.'),
        ('Conociendo el número 3', '3', '🔺', 'Escucha y traza el número tres.'),
        ('Conociendo el número 4', '4', '🚗', 'Escucha y traza el número cuatro.'),
        ('Conociendo el número 5', '5', '🖐️', 'Escucha y traza el número cinco.'),
        ('Conociendo el número 6', '6', '🐞', 'Escucha y traza el número seis.'),
        ('Conociendo el número 7', '7', '🌈', 'Escucha y traza el número siete.'),
        ('Conociendo el número 8', '8', '🐙', 'Escucha y traza el número ocho.'),
        ('Conociendo el número 9', '9', '🎈', 'Escucha y traza el número nueve.'),
        ('Conociendo el número 10', '10', '🔟', 'Escucha y traza el número diez.'),
    ],
    'Colores': [
        ('El color rojo', 'ROJO', '🔴', 'Escucha la palabra rojo. Observa el círculo y traza la palabra.'),
        ('El color azul', 'AZUL', '🔵', 'Escucha la palabra azul. Observa el círculo y traza la palabra.'),
        ('El color amarillo', 'AMARILLO', '🟡', 'Escucha la palabra amarillo. Observa el círculo y traza la palabra.'),
        ('El color verde', 'VERDE', '🟢', 'Escucha la palabra verde. Observa el círculo y traza la palabra.'),
        ('El color naranja', 'NARANJA', '🟠', 'Escucha la palabra naranja. Observa el círculo y traza la palabra.'),
        ('El color morado', 'MORADO', '🟣', 'Escucha la palabra morado. Observa el círculo y traza la palabra.'),
        ('El color rosa', 'ROSA', '🩷', 'Escucha la palabra rosa. Observa el círculo y traza la palabra.'),
        ('El color café', 'CAFE', '🟤', 'Escucha la palabra café. Observa el círculo y traza la palabra.'),
        ('El color blanco', 'BLANCO', '⚪', 'Escucha la palabra blanco. Observa el círculo y traza la palabra.'),
        ('El color negro', 'NEGRO', '⚫', 'Escucha la palabra negro. Observa el círculo y traza la palabra.'),
    ],
    'Palabras': [
        ('La palabra mamá', 'MAMA', '👩', 'Escucha mamá. Observa sus letras y traza la palabra.'),
        ('La palabra papá', 'PAPA', '👨', 'Escucha papá. Observa sus letras y traza la palabra.'),
        ('La palabra casa', 'CASA', '🏠', 'Escucha casa. Observa sus letras y traza la palabra.'),
        ('La palabra mesa', 'MESA', '🪑', 'Escucha mesa. Observa sus letras y traza la palabra.'),
        ('La palabra mano', 'MANO', '✋', 'Escucha mano. Observa sus letras y traza la palabra.'),
        ('La palabra luna', 'LUNA', '🌙', 'Escucha luna. Observa sus letras y traza la palabra.'),
        ('La palabra gato', 'GATO', '🐈', 'Escucha gato. Observa sus letras y traza la palabra.'),
        ('La palabra perro', 'PERRO', '🐕', 'Escucha perro. Observa sus letras y traza la palabra.'),
        ('La palabra agua', 'AGUA', '💧', 'Escucha agua. Observa sus letras y traza la palabra.'),
        ('La palabra pelota', 'PELOTA', '⚽', 'Escucha pelota. Observa sus letras y traza la palabra.'),
    ],
}


def seed_lessons(apps, schema_editor):
    Modulo = apps.get_model('academia', 'Modulo')
    Leccion = apps.get_model('academia', 'Leccion')
    Actividad = apps.get_model('academia', 'Actividad')

    for module_order, (module_name, lessons) in enumerate(CATALOGO.items(), start=1):
        modulo = Modulo.objects.filter(nombre__iexact=module_name).first()
        if modulo is None:
            modulo = Modulo.objects.create(nombre=module_name, orden=module_order)

        for lesson_order, (title, target, emoji, instruction) in enumerate(lessons, start=1):
            leccion, _ = Leccion.objects.get_or_create(
                modulo=modulo,
                orden=lesson_order,
                defaults={'titulo': title, 'nivel': 1 if lesson_order <= 5 else 2},
            )
            if not Actividad.objects.filter(leccion=leccion).exists():
                Actividad.objects.create(
                    leccion=leccion,
                    tipo='trazo',
                    instruccion_audio=instruction,
                    contenido={
                        'objetivo': target,
                        'letra': target,
                        'palabra': target,
                        'imagen_emoji': emoji,
                        'descripcion_visual': instruction,
                        'tipo_objetivo': 'letra' if len(target) == 1 else 'palabra',
                    },
                    orden=1,
                )


def reverse_seed(apps, schema_editor):
    # No eliminar contenido: una persona puede haber comenzado a usarlo.
    pass


class Migration(migrations.Migration):
    dependencies = [('academia', '0004_normalizar_tipos_actividad')]
    operations = [migrations.RunPython(seed_lessons, reverse_seed)]
