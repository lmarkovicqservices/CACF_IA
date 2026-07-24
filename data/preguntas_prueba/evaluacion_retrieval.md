# Evaluación de retrieval (recall@3)

## 1. el silo autoconsumo conviene para el tambo?

- Esperado: ['Autoconsumo.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Autoconsumo.docx']
- Resultado: **OK**

## 2. que cuidados hay que tener con el autoconsumo para que no pierda calidad?

- Esperado: ['Autoconsumo.docx']
- Traído (top-3): ['Autoconsumo.docx', 'Henolaje.docx']
- Resultado: **OK**

## 3. con que humedad se cosecha el earlage?

- Esperado: ['Earlage.docx']
- Traído (top-3): ['Earlage.docx']
- Resultado: **OK**

## 4. como es el proceso de henificación?

- Esperado: ['Henificación.docx']
- Traído (top-3): ['Henificación.docx', 'Henolaje.docx']
- Resultado: **OK**

## 5. con cuanta humedad puedo enfardar para que no se me prenda fuego el rollo después?

- Esperado: ['Henificación.docx']
- Traído (top-3): ['Henolaje.docx']
- Resultado: **FALLA**
- Causa probable: ambigüedad real: "rollo" y "humedad" aparecen tanto en Henificación.docx como en Henolaje.docx, ambos hablan de forraje enrollado.

## 6. cual es la diferencia entre henolaje y silaje?

- Esperado: ['Henolaje.docx', 'Silajes.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Henolaje.docx']
- Resultado: **OK**

## 7. a que humedad se hace el henolaje?

- Esperado: ['Henolaje.docx']
- Traído (top-3): ['Henolaje.docx', 'Henificación.docx']
- Resultado: **OK**

## 8. Hay que tapar el silo? y que que pasa si lo tapo mal=

- Esperado: ['IMPORTANCIA DEL TAPADO DE LOS SILOS.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Autoconsumo.docx', 'IMPORTANCIA DEL TAPADO DE LOS SILOS.docx']
- Resultado: **OK**

## 9. para que sirven los inoculantes en el silaje?

- Esperado: ['Inoculantes para ensilaje.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx']
- Resultado: **OK**

## 10. que inoculante me conviene usar?

- Esperado: ['Inoculantes para ensilaje.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx']
- Resultado: **OK**

## 11. como se si mi silo fermentó bien?

- Esperado: ['Interpretación de los silos.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Autoconsumo.docx', 'IMPORTANCIA DEL TAPADO DE LOS SILOS.docx']
- Resultado: **FALLA**
- Causa probable: vocabulario genérico: "silo" y "fermentó" son términos usados en casi todos los documentos del corpus, no distinguen Interpretación de los silos.docx.

## 12. que olorindica que el silo está podrido?

- Esperado: ['Interpretación de los silos.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Autoconsumo.docx']
- Resultado: **FALLA**
- Causa probable: typo en la pregunta: "olorindica" (sin espacio) no matchea con "olor" ni "indica" por separado, se pierde la palabra clave más específica.

## 13. que es la capa negra del silo?

- Esperado: ['La capa negra y sus consecuencias.docx']
- Traído (top-3): ['La capa negra y sus consecuencias.docx', 'Inoculantes para ensilaje.docx', 'Autoconsumo.docx']
- Resultado: **OK**

## 14. es peligroso darle a los animales silaje con capa negra?

- Esperado: ['La capa negra y sus consecuencias.docx']
- Traído (top-3): ['Autoconsumo.docx', 'Inoculantes para ensilaje.docx']
- Resultado: **FALLA**
- Causa probable: sesgo por tamaño: aunque "capa"+"negra" son específicos, la pregunta también repite "silaje"/"animales", términos genéricos que favorecen a documentos grandes como Autoconsumo.docx e Inoculantes para ensilaje.docx.

## 15. que son las micotoxinas?

- Esperado: ['micotoxinas.docx']
- Traído (top-3): ['micotoxinas.docx']
- Resultado: **OK**

## 16. como evito que se me formen micotoxinas?

- Esperado: ['micotoxinas.docx']
- Traído (top-3): ['micotoxinas.docx']
- Resultado: **OK**

## 17. cuales son los errores mas comunes al hacer silaje?

- Esperado: ['Pasos necesarios para la confección de silajes.docx', 'Pérdidas durante el proceso de ensilaje.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx']
- Resultado: **FALLA**
- Causa probable: sesgo por tamaño + vocabulario genérico: pregunta muy general, gana Inoculantes para ensilaje.docx (12.505 caracteres, el 2do doc más largo).

## 18. en que parte del proceso se pierde mas silaje?

- Esperado: ['Pérdidas durante el proceso de ensilaje.docx']
- Traído (top-3): ['Silajes.docx', 'Inoculantes para ensilaje.docx']
- Resultado: **FALLA**
- Causa probable: sesgo por tamaño: pierde contra Silajes.docx, el documento más largo del corpus (16.018 caracteres) que dilluye el score de Pérdidas durante el proceso de ensilaje.docx (3.580 caracteres) pese a ser el correcto.

## 19. que tengo que analizar en un forraje conservado?

- Esperado: ['Qué analizar de los forrajes conservados.docx']
- Traído (top-3): ['Qué analizar de los forrajes conservados.docx', 'Tomademuestras.docx', 'Henolaje.docx']
- Resultado: **OK**

## 20. como leo un análisis de laboratorio de silaje?

- Esperado: ['Qué analizar de los forrajes conservados.docx', 'Interpretación de los silos.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Silajes.docx', 'Tomademuestras.docx']
- Resultado: **FALLA**
- Causa probable: pregunta multi-tema: mezcla "análisis" (Qué analizar de los forrajes conservados.docx) con "interpretación" (Interpretación de los silos.docx), el score se reparte y ninguno de los dos gana.

## 21. que riesgos físicos tiene trabajar con silos aéreos?

- Esperado: ['Seguridadenelmanejodelossilos.docx']
- Traído (top-3): ['Autoconsumo.docx', 'Inoculantes para ensilaje.docx']
- Resultado: **FALLA**
- Causa probable: sesgo por tamaño: Seguridadenelmanejodelossilos.docx es el documento más CHICO del corpus (2.029 caracteres) y no puede competir en conteo de palabras contra documentos varias veces más largos.

## 22. como me cuido para no tener un accidente con el silo aéreo?

- Esperado: ['Seguridadenelmanejodelossilos.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Tomademuestras.docx', 'Autoconsumo.docx']
- Resultado: **FALLA**
- Causa probable: sesgo por tamaño: mismo caso que la pregunta anterior, el documento correcto (2.029 caracteres) es el más chico del corpus.

## 23. de que depende que un silaje salga bueno?

- Esperado: ['Silajes.docx', 'Pasos necesarios para la confección de silajes.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx']
- Resultado: **FALLA**
- Causa probable: vocabulario genérico + sesgo por tamaño: pregunta muy abierta, sin términos distintivos, gana el documento más denso en vocabulario común.

## 24. como tomo una muestra de silaje? y cada cuanto hay que muestrear?

- Esperado: ['Tomademuestras.docx']
- Traído (top-3): ['Inoculantes para ensilaje.docx', 'Pasos necesarios para la confección de silajes.docx', 'Tomademuestras.docx']
- Resultado: **OK**


## Resumen

- Preguntas evaluadas: 24 de 24 (0 sin ground truth)
- Aciertos (documento correcto en top-3): 14
- Recall@3: 58%

### Patrones observados en las fallas

- sesgo por tamaño: 4 de 10 fallas
- ambigüedad real: 1 de 10 fallas
- vocabulario genérico: 1 de 10 fallas
- typo en la pregunta: 1 de 10 fallas
- sesgo por tamaño + vocabulario genérico: 1 de 10 fallas
- pregunta multi-tema: 1 de 10 fallas
- vocabulario genérico + sesgo por tamaño: 1 de 10 fallas

El patrón dominante es el **sesgo por tamaño de documento**: al sumar conteos de palabras sin normalizar por longitud, los documentos más largos ganan aunque el documento correcto sea más corto pero más específico. Esto es exactamente lo que los embeddings semánticos (normalizados por diseño) deberían corregir.
