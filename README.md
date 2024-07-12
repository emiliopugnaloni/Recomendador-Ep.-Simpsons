***Web del Recomendador**: epugna.pythonanywhere.com

**Validacion Algoritmos**:
https://colab.research.google.com/drive/1R0DkzqHi4wCCFdlR9hsf_Qrx8Fwix1DN#scrollTo=yhebarRsBTSi

Para la validación se uso la métrica de NDCG, a partir de dividir las interacciones en 80/20. Se probaron diferentes algoritmos entrenando en train  (en varios se hizo una validacion-cruzada para elegir los mejores hiperparametros) y luego prediciendo en test. El NDCG se calculo para cada usuario usando las primeras 9 recomendaciones de cada algoritmo (ignorando los episodios de cada usuario que ya aparecían en train) y comparándolo con los episodios que le gustaron a cada usuario (rating>=4/5) en la base de test
Luego, con el NDCG de usuario por cada algoritmo en la base de Test, se analizo el promedio de la métrica por cada usuario. Para analizar la ventaja de un algoritmo sobre otro a medida en usuarios con distinta cantidad de reviews, se calculo el promedio del ndcg en distintos conjuntos de usuarios (con mas de 3,5,10,15,... reviews, y entre 0-3, 0-5,...). Esto se encuentra en el Excel

Asi, se decidió por utilizar:
- Algoritmo de recomendación no personalizada para usuarios entre 0-5 reviews
- Algoritmo de la librería lightfm, con loss=warp para usuarios con mas de 5 reviews

