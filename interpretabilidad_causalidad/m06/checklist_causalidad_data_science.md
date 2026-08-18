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

