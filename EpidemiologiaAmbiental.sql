CREATE DATABASE EpidemiologiaAmbiental;
USE EpidemiologiaAmbiental;

-- 1. Catálogo de medicamentos y sus umbrales PNEC (Concentración prevista sin efecto)
CREATE TABLE Medicamentos (
    id_med INT AUTO_INCREMENT PRIMARY KEY,
    nombre_comun VARCHAR(100) NOT NULL,
    grupo_terapeutico VARCHAR(50),
    pnec_ngl FLOAT NOT NULL, -- Umbral de toxicidad en nanogramos/litro
    impacto_salud TEXT
);

-- 2. Ubicaciones de muestreo
CREATE TABLE Puntos_Monitoreo (
    id_punto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rio VARCHAR(100) NOT NULL,
    cuenca VARCHAR(100),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    poblacion_cercana INT
);

-- 3. Registro de toma de muestras
CREATE TABLE Muestras (
    id_muestra INT AUTO_INCREMENT PRIMARY KEY,
    id_punto INT,
    fecha_recoleccion DATE,
    ph_agua FLOAT,
    temperatura_c FLOAT,
    FOREIGN KEY (id_punto) REFERENCES Puntos_Monitoreo(id_punto) ON DELETE CASCADE
);

-- 4. Resultados analíticos (N:M entre Muestras y Medicamentos)
CREATE TABLE Resultados_Laboratorio (
    id_resultado INT AUTO_INCREMENT PRIMARY KEY,
    id_muestra INT,
    id_med INT,
    concentracion_hallada FLOAT NOT NULL, -- ng/L
    FOREIGN KEY (id_muestra) REFERENCES Muestras(id_muestra) ON DELETE CASCADE,
    FOREIGN KEY (id_med) REFERENCES Medicamentos(id_med) ON DELETE CASCADE
);

INSERT INTO Medicamentos (nombre_comun, grupo_terapeutico, pnec_ngl, impacto_salud) VALUES
('Diclofenaco', 'Analgésico', 100.0, 'Daño en órganos de fauna acuática'),
('Ciprofloxacina', 'Antibiótico', 50.0, 'Resistencia bacteriana ambiental'),
('Etinilestradiol', 'Hormona', 0.1, 'Disrupción endocrina y feminización de peces'),
('Losartán', 'Antihipertensivo', 1000.0, 'Toxicidad crónica persistente');

INSERT INTO Puntos_Monitoreo (nombre_rio, cuenca, latitud, longitud, poblacion_cercana) VALUES
('Río Bogotá', 'Magdalena', 4.71, -74.07, 8000000),
('Río Medellín', 'Cauca', 6.24, -75.58, 2500000),
('Río Cauca', 'Cauca', 3.43, -76.51, 2200000);

INSERT INTO Muestras (id_punto, fecha_recoleccion, ph_agua, temperatura_c) VALUES
(1, '2024-01-15', 7.2, 18.5),
(1, '2024-02-20', 6.8, 19.0),
(2, '2024-01-18', 7.5, 22.1),
(3, '2024-01-25', 7.1, 24.5);

INSERT INTO Resultados_Laboratorio (id_muestra, id_med, concentracion_hallada) VALUES
(1, 1, 450.5), (1, 2, 120.0), -- Río Bogotá Enero
(2, 1, 380.2), (2, 3, 0.5),   -- Río Bogotá Febrero
(3, 2, 85.3),  (3, 4, 1200.0),-- Río Medellín
(4, 3, 0.2);                  -- Río Cauca


-- Consultas SQL (Análisis Epidemiológico)--
-- 1. Extracción de Riesgo Directo: Medicamentos que superan el umbral de seguridad.
SELECT m.nombre_comun, r.concentracion_hallada, m.pnec_ngl, 
(r.concentracion_hallada / m.pnec_ngl) AS cociente_riesgo
FROM Resultados_Laboratorio r
JOIN Medicamentos m ON r.id_med = m.id_med
WHERE (r.concentracion_hallada / m.pnec_ngl) > 1;

-- 2. Transformación y Promedio: Concentración promedio por grupo terapéutico.
SELECT m.grupo_terapeutico, ROUND(AVG(r.concentracion_hallada), 2) AS promedio_concentracion
FROM Medicamentos m
JOIN Resultados_Laboratorio r ON m.id_med = r.id_med
GROUP BY m.grupo_terapeutico;

-- 3. Refinamiento Geográfico: Máxima concentración por río.
SELECT p.nombre_rio, MAX(r.concentracion_hallada) as max_deteccion
FROM Puntos_Monitoreo p
JOIN Muestras mu ON p.id_punto = mu.id_punto
JOIN Resultados_Laboratorio r ON mu.id_muestra = r.id_muestra
GROUP BY p.nombre_rio;

-- 4. Subconsulta de Control: Muestras que detectaron hormonas específicamente.
SELECT * FROM Muestras 
WHERE id_muestra IN (SELECT id_muestra FROM Resultados_Laboratorio WHERE id_med = 3);

-- 5. Conteo de Impacto: Cantidad de fármacos detectados por cuenca.
SELECT p.cuenca, COUNT(r.id_med) as total_hallazgos
FROM Puntos_Monitoreo p
JOIN Muestras mu ON p.id_punto = mu.id_punto
JOIN Resultados_Laboratorio r ON mu.id_muestra = r.id_muestra
GROUP BY p.cuenca;


