"""Evaluación orientativa de trazos mediante plantillas vectoriales sencillas.

El resultado mide cercanía geométrica al recorrido de referencia. No es un
reconocedor profesional de escritura ni reemplaza la valoración pedagógica.
"""
from __future__ import annotations

import math
import unicodedata

# Cada letra/número se representa con una o varias polilíneas normalizadas.
# Las coordenadas viven en un cuadro de 0 a 1.
GLYPH_PATHS = {
    "A": [[(0.12, .92), (.50, .08), (.88, .92)], [(.28, .57), (.72, .57)]],
    "B": [[(.20, .08), (.20, .92)], [(.20, .08), (.62, .08), (.82, .20), (.82, .36), (.64, .49), (.20, .49)], [(.20, .49), (.66, .49), (.84, .64), (.84, .80), (.66, .92), (.20, .92)]],
    "C": [[(.82, .18), (.65, .08), (.34, .08), (.15, .25), (.15, .75), (.34, .92), (.65, .92), (.82, .82)]],
    "D": [[(.20, .08), (.20, .92)], [(.20, .08), (.54, .08), (.82, .26), (.88, .50), (.82, .74), (.54, .92), (.20, .92)]],
    "E": [[(.80, .08), (.20, .08), (.20, .92), (.82, .92)], [(.20, .50), (.70, .50)]],
    "F": [[(.20, .92), (.20, .08), (.82, .08)], [(.20, .49), (.70, .49)]],
    "G": [[(.82, .20), (.64, .08), (.34, .08), (.15, .25), (.15, .75), (.34, .92), (.68, .92), (.84, .76), (.84, .55), (.56, .55)]],
    "H": [[(.18, .08), (.18, .92)], [(.82, .08), (.82, .92)], [(.18, .50), (.82, .50)]],
    "I": [[(.20, .08), (.80, .08)], [(.50, .08), (.50, .92)], [(.20, .92), (.80, .92)]],
    "J": [[(.22, .08), (.82, .08)], [(.70, .08), (.70, .72), (.58, .90), (.34, .94), (.16, .80)]],
    "K": [[(.20, .08), (.20, .92)], [(.80, .08), (.20, .52), (.82, .92)]],
    "L": [[(.20, .08), (.20, .92), (.82, .92)]],
    "M": [[(.12, .92), (.12, .08), (.50, .55), (.88, .08), (.88, .92)]],
    "N": [[(.16, .92), (.16, .08), (.84, .92), (.84, .08)]],
    "O": [[(.50, .08), (.72, .12), (.86, .30), (.88, .70), (.72, .88), (.50, .92), (.28, .88), (.12, .70), (.12, .30), (.28, .12), (.50, .08)]],
    "P": [[(.20, .92), (.20, .08), (.62, .08), (.82, .22), (.82, .39), (.62, .52), (.20, .52)]],
    "Q": [[(.50, .08), (.72, .12), (.86, .30), (.88, .70), (.72, .88), (.50, .92), (.28, .88), (.12, .70), (.12, .30), (.28, .12), (.50, .08)], [(.60, .68), (.90, .98)]],
    "R": [[(.20, .92), (.20, .08), (.62, .08), (.82, .22), (.82, .39), (.62, .52), (.20, .52)], [(.52, .52), (.84, .92)]],
    "S": [[(.82, .18), (.65, .08), (.34, .08), (.16, .24), (.22, .42), (.72, .58), (.84, .76), (.66, .92), (.34, .92), (.16, .82)]],
    "T": [[(.12, .08), (.88, .08)], [(.50, .08), (.50, .92)]],
    "U": [[(.16, .08), (.16, .70), (.30, .90), (.50, .94), (.70, .90), (.84, .70), (.84, .08)]],
    "V": [[(.12, .08), (.50, .92), (.88, .08)]],
    "W": [[(.08, .08), (.28, .92), (.50, .52), (.72, .92), (.92, .08)]],
    "X": [[(.16, .08), (.84, .92)], [(.84, .08), (.16, .92)]],
    "Y": [[(.14, .08), (.50, .48), (.86, .08)], [(.50, .48), (.50, .92)]],
    "Z": [[(.14, .08), (.86, .08), (.14, .92), (.86, .92)]],
    "0": [[(.50, .08), (.72, .12), (.86, .30), (.88, .70), (.72, .88), (.50, .92), (.28, .88), (.12, .70), (.12, .30), (.28, .12), (.50, .08)]],
    "1": [[(.28, .25), (.50, .08), (.50, .92)], [(.28, .92), (.72, .92)]],
    "2": [[(.16, .24), (.32, .08), (.66, .08), (.84, .25), (.80, .42), (.16, .92), (.86, .92)]],
    "3": [[(.18, .12), (.68, .08), (.84, .26), (.64, .48), (.44, .48)], [(.64, .48), (.84, .68), (.78, .86), (.58, .94), (.18, .88)]],
    "4": [[(.68, .92), (.68, .08), (.14, .64), (.88, .64)]],
    "5": [[(.82, .08), (.24, .08), (.20, .46), (.62, .44), (.82, .60), (.80, .82), (.60, .94), (.20, .88)]],
    "6": [[(.78, .12), (.50, .08), (.24, .28), (.16, .66), (.32, .88), (.62, .92), (.82, .76), (.78, .58), (.58, .48), (.22, .56)]],
    "7": [[(.14, .08), (.86, .08), (.42, .92)]],
    "8": [[(.50, .50), (.28, .42), (.20, .22), (.36, .08), (.64, .08), (.80, .22), (.72, .42), (.50, .50), (.26, .62), (.18, .80), (.34, .94), (.66, .94), (.82, .80), (.74, .62), (.50, .50)]],
    "9": [[(.78, .48), (.42, .54), (.20, .38), (.20, .18), (.40, .08), (.68, .12), (.82, .34), (.78, .72), (.52, .92), (.24, .88)]],
}


def normalizar_objetivo(value: str) -> str:
    value = unicodedata.normalize("NFD", str(value or "").upper())
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return "".join(char for char in value if char in GLYPH_PATHS)


def _sample_path(points, step=0.018):
    samples = []
    for start, end in zip(points, points[1:]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        distance = math.hypot(dx, dy)
        count = max(1, int(math.ceil(distance / step)))
        for index in range(count):
            ratio = index / count
            samples.append((start[0] + dx * ratio, start[1] + dy * ratio))
    samples.append(tuple(points[-1]))
    return samples


def expected_strokes(target: str):
    chars = normalizar_objetivo(target)
    if not chars or len(chars) > 10:
        raise ValueError("El ejercicio debe contener entre 1 y 10 letras o números compatibles.")
    strokes = []
    slot = 1.0 / len(chars)
    for index, char in enumerate(chars):
        for path in GLYPH_PATHS[char]:
            local_samples = _sample_path(path)
            strokes.append([
                ((index + 0.5) * slot + (x - 0.5) * slot * 1.05,
                 0.08 + y * 0.84)
                for x, y in local_samples
            ])
    return strokes


def expected_points(target: str):
    return [point for stroke in expected_strokes(target) for point in stroke]


def _densify_user_points(points):
    # Limita el volumen de cálculo incluso si el navegador envía miles de muestras.
    if len(points) > 800:
        stride = int(math.ceil(len(points) / 800))
        sampled = points[::stride]
        if sampled[-1] is not points[-1]:
            sampled.append(points[-1])
        points = sampled
    result = []
    for point in points:
        x = float(point["x"])
        y = float(point["y"])
        result.append((x, y, point.get("stroke", 0)))
    dense = []
    for start, end in zip(result, result[1:]):
        if start[2] != end[2]:
            dense.append((start[0], start[1]))
            continue
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        steps = max(1, min(20, int(math.ceil(distance / 0.035))))
        for index in range(steps):
            ratio = index / steps
            dense.append((start[0] + (end[0] - start[0]) * ratio,
                          start[1] + (end[1] - start[1]) * ratio))
    if result:
        dense.append((result[-1][0], result[-1][1]))
    if len(dense) > 5000:
        stride = int(math.ceil(len(dense) / 5000))
        dense = dense[::stride]
        if result:
            dense.append((result[-1][0], result[-1][1]))
    return dense


def calcular_precision(target: str, coordinates: list[dict]) -> float:
    """Devuelve porcentaje aproximado 0..100 de cercanía al modelo vectorial."""
    expected = expected_points(target)
    drawn = _densify_user_points(coordinates)
    if len(drawn) < 2:
        raise ValueError("Dibuja el carácter antes de confirmar.")

    tolerance = 0.095
    coverage_hits = 0
    for ex, ey in expected:
        nearest = min(math.hypot(ex - x, ey - y) for x, y in drawn)
        if nearest <= tolerance:
            coverage_hits += 1
    coverage = coverage_hits / max(1, len(expected))

    proximity_hits = 0
    for x, y in drawn:
        nearest = min(math.hypot(x - ex, y - ey) for ex, ey in expected)
        if nearest <= tolerance:
            proximity_hits += 1
    proximity = proximity_hits / max(1, len(drawn))

    # Mayor peso a recorrer la forma completa; menor peso a evitar trazos fuera de ella.
    return round(max(0.0, min(100.0, (coverage * 0.68 + proximity * 0.32) * 100)), 1)
