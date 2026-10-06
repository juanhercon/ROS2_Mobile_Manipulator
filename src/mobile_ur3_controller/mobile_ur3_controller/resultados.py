import matplotlib.pyplot as plt
import numpy as np

x_real=[1.9, 2.1, 3.5, 3.7, 5.1, 5.3, 6.7, 6.9]
x_estimada=[1.893, 2.119, 3.490, 3.710, 5.107, 5.295, 6.676, 6.883]
y_real = [0.65, 0.67, 0.65, 0.67, 0.65, 0.67, 0.65, 0.67]
y_estimada=[0.814, 0.783, 0.811, 0.795, 0.804, 0.794, 0.799, 0.806]
z_real=[1, 0.95, 1, 0.95, 1, 0.95, 1, 0.95]
z_estimada=[0.988, 0.911, 0.990, 0.913, 1.005, 0.912, 1.006, 0.914]
contador = 1
list_eam =[]
list_ecm =[]
list_recm =[]
for valor in range(len(x_real)):
    
    eam = (abs(x_real[valor]-x_estimada[valor])+abs(y_real[valor]-y_estimada[valor])+abs(z_real[valor]-z_estimada[valor]))/3.0
    ecm = (pow(abs(x_real[valor]-x_estimada[valor]),2)+pow(abs(y_real[valor]-y_estimada[valor]),2)+pow(abs(z_real[valor]-z_estimada[valor]),2))/3.0
    recm = np.sqrt(ecm)
    print('Error medio absoluto del racimo ',contador,' es ',eam)
    print('Error cuadrático medio del racimo ',contador,' es ',ecm)
    print('Raiz error cuadrático medio del racimo ',contador,' es ',recm)
    contador=contador+1
    list_eam.append(eam *100)
    list_ecm.append(ecm*10000)
    list_recm.append(recm*100)

print(list_eam)
print(list_ecm)
print(list_recm)

'''Diagrama de barras'''
# Configuración del gráfico de barras
x = np.arange(len(x_real))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, list_eam, width, label='MAE (Error Absoluto Medio)', color='#3498db')
rects2 = ax.bar(x + width/2, list_recm, width, label='RMSE (Raíz Error Cuadrático Medio)', color='#e74c3c')

# Detalles visuales
ax.set_ylabel('Error (centímetros)', fontsize=12)
ax.set_title('Comparativa de Errores por fruto detectado (Posicionamiento de Frutos)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
etiquetas_frutos = [f'Fruto {i + 1}' for i in range(len(x_estimada))]
ax.set_xticklabels(etiquetas_frutos)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Añadir los valores en las barras para que sea legible
ax.bar_label(rects1, padding=3, fmt='%.1f')
ax.bar_label(rects2, padding=3, fmt='%.1f')

plt.tight_layout()
plt.show()
