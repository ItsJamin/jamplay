import numpy as np
import random
from tools.mapping import BaseMapper

class Particle:
    def __init__(self, width, height, analysis_data):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        energy = analysis_data["overall_energy"]
        tempo = analysis_data["tempo_estimate"]
        loudness = analysis_data["rms"]

        # Geschwindigkeit basierend auf Musikmerkmalen
        speed = (energy * 10 + tempo * 0.5 + loudness * 2)
        self.vx = random.uniform(-1, 1) * speed
        self.vy = random.uniform(-1, 1) * speed

        # Größere Partikelgröße: zwischen 20 und 40
        self.size = max(20, int(np.clip(loudness, 20, 40)))  # Größe erhöht auf zwischen 20 und 40
        self.life = random.uniform(0.5, 2.0)

        # Farbe basierend auf Frequenzbereichen
        self.color = self.compute_color(analysis_data)

    def compute_color(self, analysis_data):
        bass = analysis_data["bass_level"]
        mid = analysis_data["mid_level"]
        treble = analysis_data["treble_level"]

        # Frequenzen zu RGB-Farben
        r = int(np.clip(bass * 255, 0, 255))
        g = int(np.clip(mid * 255, 0, 255))
        b = int(np.clip(treble * 255, 0, 255))
        return (r, g, b)

    def update(self, analysis_data):
        # Geschwindigkeit basierend auf Musikdaten und spektralen Kontrasten anpassen
        energy = analysis_data["overall_energy"]
        contrast = analysis_data["spectral_contrast"]

        # Kleine zufällige Bewegung hinzufügen
        jitter = random.uniform(-1, 1) * contrast * 0.5
        self.vx += jitter
        self.vy += jitter

        # Position basierend auf Geschwindigkeit und Energie
        self.x += self.vx
        self.y += self.vy

        # Lebensdauer reduzieren
        self.life -= 0.02

    def is_alive(self):
        return self.life > 0


class ParticleMapper(BaseMapper):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.particles = []  # Liste für Partikel

    def map(self, analysis_data):
        output = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        energy = analysis_data["overall_energy"]
        flux = analysis_data["spectral_flux"]
        is_beat = analysis_data["is_beat"]
        is_silent = analysis_data["is_silent"]

        # Berechnung der Partikelanzahl:
        spawn_base = energy * 30  # Basisanzahl der Partikel
        spawn_flux = flux * 5  # Einfluss des spektralen Flux
        spawn_beat = 10 if is_beat else 0  # Zusätzliche Partikel bei Beat
        spawn_count = spawn_base + spawn_flux + spawn_beat

        # Zufallsfaktor einfügen: spawn_count zwischen einem Bereich
        # Stellen Sie sicher, dass spawn_count im Durchschnitt kleiner als 50 bleibt
        spawn_count = int(np.clip(spawn_count, 0, 50))  # Maximal 50 Partikel

        # Zufällige Modulation zwischen 60% und 100% der spawn_count für Variabilität
        spawn_count = 50 - int(spawn_count * random.uniform(0.6, 1.0))

        # Debug: Ausgabe der Anzahl der Partikel
        print(f"Spawning {spawn_count} particles...")

        # Partikel nur bei nicht-stille erzeugen
        if not is_silent:
            for _ in range(spawn_count):
                self.particles.append(Particle(self.width, self.height, analysis_data))

        # Aktualisieren und Entfernen von toten Partikeln
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update(analysis_data)

        # Partikel auf dem Ausgabebild darstellen
        for p in self.particles:
            x, y = int(p.x), int(p.y)

            # Überprüfen, ob die Partikel im sichtbaren Bereich sind
            if 0 <= x < self.width and 0 <= y < self.height:
                output[y, x] = p.color

        # Debug-Ausgabe: Stellen Sie sicher, dass die ersten 10 Partikel angezeigt werden
        if len(self.particles) > 0:
            print(f"First 10 particles: {[{'x': p.x, 'y': p.y, 'color': p.color} for p in self.particles[:10]]}")

        return output
