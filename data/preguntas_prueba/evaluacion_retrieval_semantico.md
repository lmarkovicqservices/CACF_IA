# Evaluación de retrieval semántico (recall@3)

## 1. el silo autoconsumo conviene para el tambo?

- Esperado: ['Autoconsumo.docx']
- Traído (top-3): ['Autoconsumo.docx']
- Resultado: **OK**

## 2. que cuidados hay que tener con el autoconsumo para que no pierda calidad?

- Esperado: ['Autoconsumo.docx']
- Traído (top-3): ['Autoconsumo.docx', 'micotoxinas.docx']
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

## 6. cual es la diferencia entre henolaje y silaje?

- Esperado: ['Henolaje.docx', 'Silajes.docx']
- Traído (top-3): ['Henolaje.docx', 'Silajes.docx', 'Henificación.docx']
- Resultado: **OK**

## 7. a que humedad se hace el henolaje?

- Esperado: ['Henolaje.docx']
- Traído (top-3): ['Henolaje.docx', 'Henificación.docx']
- Resultado: **OK**

## 8. Hay que tapar el silo? y que que pasa si lo tapo mal=

- Esperado: ['IMPORTANCIA DEL TAPADO DE LOS SILOS.docx']
- Traído (top-3): ['IMPORTANCIA DEL TAPADO DE LOS SILOS.docx', 'La capa negra y sus consecuencias.docx']
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
- Traído (top-3): ['Interpretación de los silos.docx', 'Tomademuestras.docx']
- Resultado: **OK**

## 12. que olorindica que el silo está podrido?

- Esperado: ['Interpretación de los silos.docx']
- Traído (top-3): ['Interpretación de los silos.docx']
- Resultado: **OK**

## 13. que es la capa negra del silo?

- Esperado: ['La capa negra y sus consecuencias.docx']
- Traído (top-3): ['La capa negra y sus consecuencias.docx']
- Resultado: **OK**

## 14. es peligroso darle a los animales silaje con capa negra?

- Esperado: ['La capa negra y sus consecuencias.docx']
- Traído (top-3): ['La capa negra y sus consecuencias.docx', 'Interpretación de los silos.docx']
- Resultado: **OK**

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
- Traído (top-3): ['Silajes.docx', 'Autoconsumo.docx', 'Pasos necesarios para la confección de silajes.docx']
- Resultado: **OK**

## 18. en que parte del proceso se pierde mas silaje?

- Esperado: ['Pérdidas durante el proceso de ensilaje.docx']
- Traído (top-3): ['Pérdidas durante el proceso de ensilaje.docx', 'IMPORTANCIA DEL TAPADO DE LOS SILOS.docx']
- Resultado: **OK**

## 19. que tengo que analizar en un forraje conservado?

- Esperado: ['Qué analizar de los forrajes conservados.docx']
- Traído (top-3): ['Tomademuestras.docx', 'Qué analizar de los forrajes conservados.docx']
- Resultado: **OK**

## 20. como leo un análisis de laboratorio de silaje?

- Esperado: ['Qué analizar de los forrajes conservados.docx', 'Interpretación de los silos.docx']
- Traído (top-3): ['Tomademuestras.docx', 'Qué analizar de los forrajes conservados.docx']
- Resultado: **OK**

## 21. que riesgos físicos tiene trabajar con silos aéreos?

- Esperado: ['Seguridadenelmanejodelossilos.docx']
- Traído (top-3): ['Seguridadenelmanejodelossilos.docx', 'Tomademuestras.docx']
- Resultado: **OK**

## 22. como me cuido para no tener un accidente con el silo aéreo?

- Esperado: ['Seguridadenelmanejodelossilos.docx']
- Traído (top-3): ['Seguridadenelmanejodelossilos.docx', 'Tomademuestras.docx']
- Resultado: **OK**

## 23. de que depende que un silaje salga bueno?

- Esperado: ['Silajes.docx', 'Pasos necesarios para la confección de silajes.docx']
- Traído (top-3): ['Silajes.docx', 'Pasos necesarios para la confección de silajes.docx']
- Resultado: **OK**

## 24. como tomo una muestra de silaje? y cada cuanto hay que muestrear?

- Esperado: ['Tomademuestras.docx']
- Traído (top-3): ['Tomademuestras.docx']
- Resultado: **OK**


## Resumen

- Preguntas evaluadas: 24 de 24
- Aciertos (documento correcto en top-3): 23
- Recall@3 semántico: 96%
- Recall@3 keyword (baseline anterior): 58%
- Mejora: +38 puntos porcentuales
