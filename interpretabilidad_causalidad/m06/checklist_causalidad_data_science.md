# Checklist causal para proyectos de Data Science

Esta guia sirve como recordatorio practico para proyectos donde no basta con predecir bien, sino que queremos interpretar correctamente una relacion o defender una intervencion.

La pregunta central es:

> Si cambio una accion, politica, tratamiento o decision, que pasa con el resultado?

## 1. Flujo mental

Antes de modelar, separar tres tipos de preguntas:

```text
Prediccion:
  Puedo anticipar Y?

Interpretabilidad:
  Que variables usa el modelo para predecir Y?

Causalidad:
  Que pasaria con Y si intervengo sobre D?
```

Un buen modelo predictivo no implica una conclusion causal valida.

Flujo recomendado:

```text
1. Definir la intervencion o tratamiento D.
2. Definir el resultado Y.
3. Definir las covariables pretratamiento X.
4. Dibujar un DAG plausible.
5. Identificar posibles confusores.
6. Identificar variables que no deben ajustarse.
7. Determinar conjunto backdoor.
8. Revisar solapamiento/positividad.
9. Estimar con mas de un metodo.
10. Comparar sensibilidad.
11. Declarar supuestos y limites.
```

## 2. Preguntas que debo hacerme

### Pregunta causal

```text
Que intervencion estoy evaluando?
```

Ejemplos:

```text
Enviar una campana.
Aumentar linea de credito.
Tomar un curso.
Activar una feature.
Dar un descuento.
Cambiar precio.
```

### Tratamiento

```text
Cual es D?
D es binaria, continua, ordinal o multivaluada?
El tratamiento ocurre antes del resultado?
```

### Resultado

```text
Cual es Y?
Y ocurre despues de D?
Estoy usando un proxy razonable del outcome real?
```

### Covariables

```text
Que variables existian antes del tratamiento?
Que variables podrian afectar tanto D como Y?
Que variables son proxies de seleccion al tratamiento?
```

### Variables peligrosas

```text
Estoy ajustando por algo posterior al tratamiento?
Estoy ajustando por un mediador?
Estoy ajustando por un collider?
Estoy usando IDs, fuentes, timestamps o etiquetas que filtran informacion?
```

### Comparabilidad

```text
Los tratados y controles se parecen?
Hay controles comparables para los tratados?
Hay tratados comparables para los controles?
Los propensity scores estan cerca de 0 o 1?
```

### Interpretacion

```text
Mi resultado es estable entre metodos?
El signo cambia entre crudo y ajustado?
El estimador depende de pesos extremos?
Que supuesto destruiria mi conclusion si falla?
```

## 3. Checklist de auditoria causal

Usar esta lista antes de afirmar impacto causal.

```text
[ ] Defini D claramente.
[ ] Defini Y claramente.
[ ] Verifique que D ocurre antes que Y.
[ ] Separe covariables pretratamiento de variables postratamiento.
[ ] Dibuje un DAG plausible.
[ ] Identifique confusores.
[ ] Identifique posibles colliders.
[ ] Identifique posibles mediadores.
[ ] Defini un conjunto backdoor.
[ ] Exclui IDs, source flags y variables de fuga.
[ ] Exclui outcomes o proxies posteriores como covariables.
[ ] Revise balance entre tratados y controles.
[ ] Revise solapamiento/positividad.
[ ] Estime al menos un modelo crudo y uno ajustado.
[ ] Compare metodos: regresion, IPW, matching, DML u otros.
[ ] Revise sensibilidad a pesos extremos.
[ ] Declare ignorabilidad condicional si aplica.
[ ] Declare limites por confusores no observados.
[ ] No confundi explicacion predictiva con efecto causal.
[ ] Escribi la conclusion como "bajo estos supuestos".
```

## 4. IFs utiles para decidir el tipo de analisis

### Si el proyecto es predictivo

```text
Si mi objetivo es predecir Y,
entonces necesito buen desempeno fuera de muestra.
```

Ejemplo:

```text
Predecir churn de clientes.
Predecir probabilidad de default.
Predecir demanda.
```

Cuidado:

```text
Un feature importante para prediccion no necesariamente es causa de Y.
```

### Si el proyecto interpreta un modelo

```text
Si mi objetivo es explicar que usa el modelo,
entonces uso interpretabilidad.
```

Ejemplo:

```text
SHAP dice que ingreso, deuda y antiguedad pesan en una prediccion de credito.
```

Cuidado:

```text
SHAP explica el comportamiento del modelo, no necesariamente el mundo.
```

### Si el proyecto recomienda una intervencion

```text
Si quiero cambiar D para mejorar Y,
entonces necesito analisis causal.
```

Ejemplo:

```text
Enviar una promocion para aumentar compras.
Dar capacitacion para aumentar ingresos.
Subir linea de credito para aumentar uso.
```

Cuidado:

```text
La gente que recibe D puede ser distinta desde antes.
```

### Si tengo experimento aleatorizado

```text
Si D fue asignado aleatoriamente,
entonces la identificacion causal es mas fuerte.
```

Cuidado:

```text
Todavia debo revisar incumplimiento, attrition, interferencia y balance.
```

### Si tengo datos observacionales

```text
Si D no fue aleatorizado,
entonces necesito justificar el conjunto de ajuste.
```

Cuidado:

```text
El resultado depende de ignorabilidad condicional dado X.
```

### Si el efecto crudo y el ajustado cambian de signo

```text
Si el signo cambia al ajustar,
entonces puede haber confusores, Simpson o diferencias de composicion.
```

Cuidado:

```text
No asumir que el ajustado es correcto automaticamente. Revisar DAG.
```

### Si IPW genera pesos extremos

```text
Si los pesos son extremos,
entonces hay problemas de positividad practica.
```

Cuidado:

```text
El estimador puede depender de pocas observaciones.
```

### Si DML da un resultado distinto a regresion lineal

```text
Si DML cambia el estimado,
entonces los modelos flexibles pueden estar capturando no linealidades o interacciones.
```

Cuidado:

```text
DML no arregla confusores no observados ni mal solapamiento.
```

## 5. Ejemplos por dominio

### Marketing

Pregunta causal:

```text
Enviar campana causa mas compras?
```

Riesgo:

```text
La campana se envia a clientes que ya eran mas propensos a comprar.
```

Checklist especifico:

```text
D = recibir campana
Y = compra posterior
X = historial antes de la campana
No ajustar por clics posteriores si son mediadores
Revisar si hay clientes similares que no recibieron campana
```

### Credito

Pregunta causal:

```text
Aumentar linea de credito causa mayor morosidad?
```

Riesgo:

```text
La linea se aumenta a clientes seleccionados por riesgo o buen comportamiento previo.
```

Checklist especifico:

```text
D = aumento de linea
Y = morosidad futura
X = score, ingreso, deuda, historial previo
No ajustar por uso posterior de la linea si es mediador
Revisar solapamiento entre clientes con y sin aumento
```

### Educacion

Pregunta causal:

```text
Tomar un curso aumenta ingresos o aprobacion?
```

Riesgo:

```text
Quienes toman el curso pueden tener mayor motivacion o mejores condiciones previas.
```

Checklist especifico:

```text
D = tomar curso
Y = ingreso/aprobacion posterior
X = edad, educacion previa, desempeno previo, contexto
No ajustar por variables posteriores al curso
Declarar limites por motivacion no observada
```

### Producto digital

Pregunta causal:

```text
Activar una feature aumenta retencion?
```

Riesgo:

```text
Los usuarios que usan la feature pueden ser usuarios mas avanzados desde antes.
```

Checklist especifico:

```text
D = uso/acceso a feature
Y = retencion futura
X = actividad previa, antiguedad, plan, canal, segmento
No ajustar por actividad posterior si es consecuencia de la feature
Preferir A/B test si es posible
```

## 6. Advertencias permanentes

```text
Causalidad no sale automaticamente de un modelo.
Un alto R2 o AUC no prueba impacto causal.
Una variable importante en SHAP no necesariamente es causa.
Controlar por mas variables no siempre es mejor.
No ajustar por colliders.
No ajustar por mediadores si se busca efecto total.
No usar variables postratamiento como si fueran pretratamiento.
No usar IDs, sources o flags que codifiquen tratamiento/control.
Sin solapamiento, el efecto requiere extrapolacion.
Sin ignorabilidad, el efecto puede estar sesgado.
```

## 7. Frase de cierre para reportes

Usar una conclusion de este estilo:

```text
Bajo el DAG propuesto, asumiendo ignorabilidad condicional dado X y suficiente solapamiento entre tratados y controles, estimamos que D tiene un efecto de aproximadamente ___ sobre Y. La comparacion cruda difiere de la ajustada, lo que sugiere confusión/diferencias de composicion. Los resultados deben interpretarse como evidencia causal bajo estos supuestos, no como prueba definitiva.
```

## 8. Prompts reutilizables para mantener calidad

Estos prompts estan pensados para usarse al iniciar proyectos futuros. La idea es no depender de memoria, contexto previo o intuicion del momento. Copia el prompt que corresponda y reemplaza los campos entre corchetes.

### Prompt inicial completo para arrancar un proyecto

Usar este prompt cuando el proyecto apenas empieza, incluso si todavia no hay datos o si no esta claro si sera descriptivo, predictivo, interpretativo o causal.

```text
Actua como arquitecto senior de un proyecto de Data Science con enfoque en interpretabilidad y causalidad.

Quiero iniciar un nuevo proyecto y necesito que me ayudes a estructurarlo correctamente desde cero, antes de escribir codigo.

Contexto inicial:
- Tema o problema: [describe el problema]
- Objetivo de negocio o investigacion: [que quiero decidir, mejorar o entender]
- Estado de los datos: [no tengo datos / tengo CSV / tengo TXT / tengo base SQL / tengo APIs / tengo documentos / no se todavia]
- Archivos disponibles: [lista archivos si existen]
- Unidad de analisis esperada: [cliente, usuario, transaccion, persona, producto, tienda, fecha, etc.]
- Decision o intervencion posible: [si existe]
- Resultado que me interesa: [si existe]
- Restricciones: [tiempo, herramientas, privacidad, entrega, formato final]
- Audiencia del proyecto: [tecnica, negocio, academica, regulatoria]

Antes de proponer modelos o codigo, ayudame a estudiar el caso.

Haz lo siguiente:

1. Reformula el problema en lenguaje claro.
2. Dime si el proyecto parece:
   - descriptivo
   - predictivo
   - interpretativo
   - causal
   - mixto
3. Identifica que informacion falta para decidir el enfoque.
4. Si tengo datos, propon como inspeccionarlos:
   - estructura
   - columnas
   - tipos
   - nulos
   - duplicados
   - unidad de analisis
   - temporalidad
   - posibles variables de fuga
5. Si no tengo datos, dime que datos minimos necesito recolectar.
6. Propón una estructura de carpetas para el proyecto.
7. Propón el notebook inicial y sus secciones.
8. Identifica posibles preguntas analiticas.
9. Si hay una posible intervencion, define tentativamente:
   - tratamiento D
   - resultado Y
   - covariables X
   - variables que podrian ser peligrosas
10. Propón un primer DAG conceptual si aplica.
11. Dime que analisis exploratorio seria necesario antes de modelar.
12. Dime que modelos serian candidatos, pero sin implementarlos todavia.
13. Dime que riesgos metodologicos debo cuidar.
14. Propón un plan por fases:
   - comprension del problema
   - inventario de datos
   - EDA
   - definicion causal/predictiva
   - modelado
   - validacion
   - interpretacion
   - entrega
15. Termina con una checklist de decisiones que debo confirmar antes de escribir codigo.

No empieces a programar hasta que el problema, los datos, la unidad de analisis, la temporalidad y el objetivo esten claros.
```

### Prompt maestro: auditoria causal completa

```text
Actua como auditor causal senior para un proyecto de Data Science.

Contexto del proyecto:
- Objetivo de negocio: [describe el objetivo]
- Dataset disponible: [describe tablas, columnas o adjunta esquema]
- Posible tratamiento/intervencion D: [variable o accion]
- Posible resultado Y: [variable outcome]
- Unidad de analisis: [cliente, usuario, transaccion, persona, tienda, etc.]
- Ventana temporal: [fechas y orden de eventos]

Quiero que me ayudes a decidir si puedo hacer una lectura causal o si solo debo hacer una lectura predictiva/descriptiva.

Haz lo siguiente:
1. Identifica D, Y y unidad de analisis.
2. Clasifica variables como pretratamiento, postratamiento, posibles confusores, mediadores, colliders, outcomes o variables de fuga.
3. Propone un DAG causal plausible en texto y, si aplica, en Mermaid.
4. Determina un conjunto de ajuste/backdoor razonable.
5. Lista variables que NO debo controlar y por que.
6. Indica si hay riesgo de positividad/solapamiento.
7. Recomienda estimadores apropiados: diferencia cruda, regresion ajustada, IPW, matching, DML u otros.
8. Especifica que diagnosticos debo correr.
9. Redacta una conclusion provisional bajo supuestos.
10. Lista los supuestos que, si fallan, invalidan la conclusion.

No asumas causalidad automaticamente. Si falta informacion temporal o de diseno, dilo explicitamente.
```

### Prompt para no confundir prediccion con causalidad

```text
Tengo un modelo predictivo para [Y] usando estas variables: [lista de variables].

Quiero saber si puedo interpretar la importancia de variables como efectos causales.

Analiza:
1. Que variables pueden ser solo predictoras y no causas.
2. Que variables podrian ser proxies de seleccion, fuga de informacion o postratamiento.
3. Que pregunta causal tendria sentido formular, si existe.
4. Que tratamiento D y outcome Y deberia definir.
5. Que informacion adicional necesito para pasar de prediccion a causalidad.
6. Que conclusiones NO debo afirmar con el modelo actual.

Responde con una separacion clara entre:
- Interpretabilidad del modelo.
- Hipotesis causal.
- Evidencia que falta.
```

### Prompt para construir DAG

```text
Ayudame a construir un DAG causal para este problema.

Contexto:
- Tratamiento D: [D]
- Resultado Y: [Y]
- Variables disponibles: [lista]
- Orden temporal conocido: [describe que ocurre antes/despues]
- Mecanismo de asignacion del tratamiento: [aleatorio, decision de negocio, seleccion del usuario, politica, etc.]

Tareas:
1. Propone nodos del DAG.
2. Propone flechas causales plausibles.
3. Identifica caminos backdoor entre D y Y.
4. Identifica confusores.
5. Identifica mediadores.
6. Identifica colliders.
7. Dime que variables debo ajustar y cuales debo evitar.
8. Dame una version Mermaid del DAG.
9. Explica que supuestos no pueden verificarse solo con datos.

No incluyas variables como ajuste solo porque estan disponibles. Justifica cada variable por su rol causal.
```

### Prompt para revisar variables prohibidas

```text
Revisa esta lista de variables y dime cuales NO debo usar como covariables en un analisis causal.

Tratamiento D: [D]
Resultado Y: [Y]
Variables disponibles:
[pega lista de columnas con descripcion si existe]

Para cada variable, clasificala como:
- pretratamiento valida
- posible confusor
- mediador
- collider
- postratamiento
- outcome o proxy del outcome
- identificador/fuga
- variable de seleccion/source
- no clara

Devuelve una tabla con:
1. variable
2. clasificacion
3. usar en ajuste: si/no/depende
4. razon
5. riesgo si se usa mal

Se estricto con IDs, timestamps posteriores, source flags, variables derivadas del outcome y variables posteriores al tratamiento.
```

### Prompt para revisar solapamiento y positividad

```text
Quiero auditar positividad/solapamiento para un analisis causal.

Tratamiento D: [D]
Covariables de ajuste X: [X]
Dataset: [describe o adjunta resumen]

Ayudame a:
1. Definir el propensity score e(X) = P(D=1 | X).
2. Proponer graficos para comparar distribuciones de e(X) entre tratados y controles.
3. Proponer metricas: min, max, percentiles, pesos extremos, SMD antes/despues.
4. Decidir cuando hay falta de solapamiento practico.
5. Explicar como reportar el problema sin exagerar ni esconderlo.
6. Recomendar acciones: trimming, overlap weights, cambiar estimando a ATT, o limitar poblacion.

Incluye texto de interpretacion para un reporte ejecutivo.
```

### Prompt para elegir estimador causal

```text
Tengo definido:
- D = [tratamiento]
- Y = [resultado]
- X = [covariables]
- Diseno: [experimental / observacional / cuasi-experimental / no claro]
- Tamano de muestra: [n]
- Riesgos conocidos: [positividad, confusores no observados, pesos extremos, etc.]

Ayudame a elegir estimadores causales apropiados.

Compara:
1. diferencia cruda
2. regresion ajustada/modelo de resultados
3. IPW
4. matching
5. doubly robust
6. Double Machine Learning

Para cada metodo dime:
- que estima
- supuestos principales
- ventajas
- riesgos
- diagnosticos necesarios
- cuando NO usarlo

Termina con una recomendacion practica para este caso.
```

### Prompt para conectar FWL, Simpson y ajuste

```text
Quiero saber si en mi proyecto hay una situacion tipo paradoja de Simpson.

Variables:
- D o X principal: [variable]
- Y: [resultado]
- Z o covariables de ajuste: [variables]

Analiza:
1. Asociacion cruda: Y ~ D.
2. Asociacion ajustada: Y ~ D + Z.
3. Si el signo, magnitud o conclusion cambia.
4. Explica el cambio usando Frisch-Waugh-Lovell:
   - residualizar Y respecto de Z
   - residualizar D respecto de Z
   - regresar resid(Y) sobre resid(D)
5. Dime si el cambio sugiere confusión, Simpson o diferencias de composicion.
6. Advierte que FWL es algebra lineal y que el DAG decide si ajustar por Z es causalmente correcto.

Quiero una explicacion entendible para un notebook de Data Science.
```

### Prompt para Double Machine Learning

```text
Quiero estimar un ATE con Double Machine Learning.

Definiciones:
- Tratamiento D: [D]
- Resultado Y: [Y]
- Covariables X: [X]
- Dataset/tamano: [n, columnas]

Ayudame a disenar el DML:
1. Formula el modelo parcialmente lineal:
   Y = theta D + g(X) + error
   D = m(X) + ruido
2. Explica por que DML extiende FWL.
3. Recomienda modelos auxiliares para g(X) y m(X).
4. Justifica si usar Random Forest, Gradient Boosting, Lasso, Ridge u otro.
5. Incluye cross-fitting y explica por que es necesario.
6. Define diagnosticos:
   - desempeno out-of-fold de g(X)
   - AUC/calibracion de m(X)
   - distribucion de propensity
   - residuales
   - comparacion con estimadores previos
7. Explica limites: DML no arregla confusores no observados ni falta de positividad.
8. Redacta una interpretacion final bajo supuestos.

Evita presentarlo como caja negra. Conectalo con la pregunta causal y con el DAG.
```

### Prompt para redactar conclusiones causales

```text
Ayudame a redactar una conclusion causal prudente para un reporte.

Resultados:
- Tratamiento D: [D]
- Outcome Y: [Y]
- Estimadores obtenidos: [tabla o lista]
- DAG/conjunto de ajuste: [describe]
- Diagnosticos de positividad/balance: [describe]
- Limitaciones: [describe]

Redacta:
1. Conclusion principal en lenguaje claro.
2. Que estimador tomaria como referencia y por que.
3. Como interpretar diferencias entre estimadores.
4. Supuestos necesarios.
5. Advertencias sobre lo que no puede concluirse.
6. Recomendacion para siguiente paso: experimento, mas datos, sensibilidad, monitoreo, etc.

Usa lenguaje tipo:
\"Bajo estos supuestos...\"
\"La evidencia sugiere...\"
\"No debe interpretarse como prueba definitiva...\"
```

### Prompt para auditar un notebook causal antes de entrega

```text
Revisa este notebook como auditor causal y metodologico.

Objetivo del notebook:
[describe]

Quiero que revises:
1. Si D, Y y X estan claramente definidos.
2. Si hay variables prohibidas en el ajuste.
3. Si el DAG esta alineado con los modelos.
4. Si el conjunto backdoor esta justificado.
5. Si se revisa solapamiento/positividad.
6. Si los estimadores estan bien interpretados.
7. Si hay riesgo de sobreclaim causal.
8. Si las conclusiones declaran supuestos.
9. Si el codigo es reproducible.
10. Si faltan graficos o diagnosticos esenciales.

Devuelve:
- hallazgos criticos
- mejoras recomendadas
- texto sugerido para corregir conclusiones
- checklist final de entrega
```

### Prompt para actualizar contexto al cambiar de proyecto

```text
Estoy iniciando un nuevo proyecto y quiero mantener la misma calidad causal que en analisis anteriores.

Primero, hazme preguntas para reconstruir el contexto minimo:
1. Cual es la decision/intervencion?
2. Cual es el resultado?
3. Cual es la unidad de analisis?
4. Cual es el orden temporal?
5. Como se asigna el tratamiento?
6. Que variables existian antes del tratamiento?
7. Que variables ocurren despues?
8. Que sesgos de seleccion son plausibles?
9. Que datos faltan?
10. Que conclusion quiere defender el negocio?

No propongas modelos hasta tener claro D, Y, X, temporalidad y mecanismo de asignacion.
```

## 9. Prompt corto de emergencia

Si tienes poco tiempo, usar este:

```text
Audita causalmente este proyecto antes de modelar.

D = [tratamiento]
Y = [resultado]
Columnas = [lista]
Contexto = [descripcion]

Dime:
1. Que variables puedo ajustar.
2. Que variables NO debo ajustar.
3. DAG plausible.
4. Backdoor set.
5. Riesgos de positividad.
6. Estimadores recomendados.
7. Supuestos.
8. Conclusion prudente bajo supuestos.

No confundas prediccion con causalidad y no asumas que mas controles siempre es mejor.
```
