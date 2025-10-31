import json
import numpy as np
from scipy.stats import norm, binom
from flask import Flask, render_template, jsonify
import io
import base64
import matplotlib
import matplotlib.pyplot as plt

# IMPORTANTE: Define o backend do Matplotlib para 'Agg'
# Isso permite que o Matplotlib rode sem uma interface gráfica (essencial para servidores)
matplotlib.use('Agg')

# --- Constantes do CEP para n=5 ---
A2 = 0.577
D3 = 0
D4 = 2.114
d2 = 2.326

app = Flask(__name__)

def create_control_chart_image(chart_type, labels, data, LSC, LC, LIC):
    """
    Cria um gráfico de controle com Matplotlib e retorna como uma string Base64.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        
        ax.plot(labels, data, marker='o', linestyle='-', color='#007bff', label=chart_type)
        
        # Linhas de Controle
        ax.axhline(y=LSC, color='#dc3545', linestyle='--', label=f'LSC = {LSC:.4f}')
        ax.axhline(y=LC, color='#28a745', linestyle='-', label=f'LC = {LC:.4f}')
        ax.axhline(y=LIC, color='#dc3545', linestyle='--', label=f'LIC = {LIC:.4f}')
        
        ax.set_title(f'Gráfico de Controle {chart_type}')
        ax.set_xlabel('Amostra')
        ax.set_ylabel('Valor')
        ax.legend(loc='upper right')
        ax.grid(True, linestyle=':', alpha=0.6)
        
        # Ajusta a rotação dos labels do eixo X
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Salva o gráfico em um buffer de memória
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Codifica a imagem em Base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        plt.close(fig) # Fecha a figura para liberar memória
        return img_base64
        
    except Exception as e:
        print(f"Erro ao criar gráfico: {e}")
        plt.close(fig)
        return None


def solve_cep_problems():
    """
    Função principal para carregar dados e resolver todas as questões do PDF.
    """
    
    # Carrega os dados do JSON
    with open('prova_pergunta_1.json', 'r') as f:
        data = json.load(f)

    samples_data = [item['Dados'] for item in data]
    labels = [str(item['Amostra']) for item in data]
    
    # --- Cálculos Iniciais (Q1) ---
    sample_means = [np.mean(sample) for sample in samples_data]  # X-barra (X̄)
    sample_ranges = [np.max(sample) - np.min(sample) for sample in samples_data] # R
    
    R_bar = np.mean(sample_ranges)   # R-barra (R̄)
    X_bar_bar = np.mean(sample_means) # X-barra-barra (X̄̄)

    # --- Resolução Questão 1.1: Limites de Controle X-R ---
    x_chart_limits = {
        "LSC": X_bar_bar + A2 * R_bar,
        "LC": X_bar_bar,
        "LIC": X_bar_bar - A2 * R_bar
    }
    r_chart_limits = {
        "LSC": D4 * R_bar,
        "LC": R_bar,
        "LIC": D3 * R_bar
    }

    # --- Geração das Imagens dos Gráficos ---
    x_chart_img = create_control_chart_image(
        'X-barra', labels, sample_means, 
        x_chart_limits["LSC"], x_chart_limits["LC"], x_chart_limits["LIC"]
    )
    r_chart_img = create_control_chart_image(
        'R', labels, sample_ranges, 
        r_chart_limits["LSC"], r_chart_limits["LC"], r_chart_limits["LIC"]
    )

    # Verifica se está sob controle
    out_of_control_x = [
        (i + 1, val) for i, val in enumerate(sample_means)
        if val > x_chart_limits["LSC"] or val < x_chart_limits["LIC"]
    ]
    out_of_control_r = [
        (i + 1, val) for i, val in enumerate(sample_ranges)
        if val > r_chart_limits["LSC"] or val < r_chart_limits["LIC"]
    ]
    is_in_control = not (out_of_control_x or out_of_control_r)

    # --- Resolução Questão 1.2: Regras de Western Electric ---
    we_rules_violations = check_western_electric_rules(sample_means, X_bar_bar, x_chart_limits["LSC"])

    # --- Resolução Questão 2: Capacidade do Processo ---
    sigma_hat = R_bar / d2
    LIE = 4.92
    LSE = 4.94
    yield_prob = norm.cdf((LSE - X_bar_bar) / sigma_hat) - norm.cdf((LIE - X_bar_bar) / sigma_hat)
    Cp = (LSE - LIE) / (6 * sigma_hat)
    Cpk = min((LSE - X_bar_bar) / (3 * sigma_hat), (X_bar_bar - LIE) / (3 * sigma_hat))
    prob_above_4_975 = 1 - norm.cdf((4.952 - X_bar_bar) / sigma_hat)

    # --- Resolução Questão 3 ---
    delta = 1.5
    n_items = 10
    min_good = 8
    p_good = norm.cdf(1.5) - norm.cdf(-4.5)
    prob_q3 = binom.sf(k=min_good - 1, n=n_items, p=p_good)

    # --- Compila todos os resultados ---
    return {
        "q1_1": {
            "x_chart_limits": x_chart_limits, # Enviando os limites para exibição de texto
            "r_chart_limits": r_chart_limits, #
            "x_chart_image": x_chart_img,     # Imagem Base64
            "r_chart_image": r_chart_img,     # Imagem Base64
            "is_in_control": is_in_control,
            "out_of_control_x": out_of_control_x,
            "out_of_control_r": out_of_control_r
        },
        "q1_2": {
            "violations": we_rules_violations
        },
        "q2": {
            "sigma_hat": sigma_hat,
            "X_bar_bar": X_bar_bar,
            "q2_1_yield": yield_prob,
            "q2_2_Cp": Cp,
            "q2_2_Cpk": Cpk,
            "q2_3_prob_above": prob_above_4_975
        },
        "q3": {
            "p_good_item": p_good,
            "prob_at_least_8": prob_q3
        }
    }

# (O resto do arquivo app.py (check_western_electric_rules, rotas Flask) 
# permanece exatamente o mesmo da resposta anterior)

def check_western_electric_rules(data, center_line, lsc):
    """
    Verifica as 4 regras principais de Western Electric com precisão,
    garantindo que as regras de zona (2 e 3) se aplicam a pontos
    do MESMO LADO da linha central.
    """
    violations = []
    n = len(data)

    # 1. Definição das Zonas
    # O desvio padrão do gráfico X-barra (sigma_x_barra) pode ser
    # estimado como (LSC - LC) / 3
    sigma_val = (lsc - center_line) / 3.0
    
    # Limites positivos
    zone_c_pos = center_line + sigma_val     # +1 sigma
    zone_b_pos = center_line + 2 * sigma_val # +2 sigma
    zone_a_pos = lsc                         # +3 sigma
    
    # Limites negativos
    zone_c_neg = center_line - sigma_val     # -1 sigma
    zone_b_neg = center_line - 2 * sigma_val # -2 sigma
    zone_a_neg = center_line - 3 * sigma_val # -3 sigma (LIC)

    for i in range(n):
        # --- Regra 1: 1 ponto fora dos limites de 3-sigma ---
        # (Verificado apenas uma vez por ponto)
        if i == 0: # Adicionado para evitar checagens múltiplas da mesma regra
            for j in range(n):
                 if data[j] > zone_a_pos or data[j] < zone_a_neg:
                    violations.append(f"Regra 1: Amostra {j+1} ({data[j]:.4f}) está fora dos limites de 3-sigma.")

        # --- Regra 2: 2 de 3 pontos consecutivos na Zona A ou além (mesmo lado) ---
        if i <= n - 3:
            points = data[i:i+3]
            count_pos = sum(1 for p in points if p > zone_b_pos) # Acima de +2 sigma
            count_neg = sum(1 for p in points if p < zone_b_neg) # Abaixo de -2 sigma
            
            if count_pos >= 2:
                violations.append(f"Regra 2: 2 de 3 pontos (amostras {i+1} a {i+3}) estão acima da Zona A (+2 sigma).")
            if count_neg >= 2:
                violations.append(f"Regra 2: 2 de 3 pontos (amostras {i+1} a {i+3}) estão abaixo da Zona A (-2 sigma).")

        # --- Regra 3: 4 de 5 pontos consecutivos na Zona B ou além (mesmo lado) ---
        if i <= n - 5:
            points = data[i:i+5]
            count_pos = sum(1 for p in points if p > zone_c_pos) # Acima de +1 sigma
            count_neg = sum(1 for p in points if p < zone_c_neg) # Abaixo de -1 sigma
            
            if count_pos >= 4:
                violations.append(f"Regra 3: 4 de 5 pontos (amostras {i+1} a {i+5}) estão acima da Zona B (+1 sigma).")
            if count_neg >= 4:
                violations.append(f"Regra 3: 4 de 5 pontos (amostras {i+1} a {i+5}) estão abaixo da Zona B (-1 sigma).")

        # --- Regra 4: 9 pontos consecutivos do mesmo lado da linha central ---
        # (O seu código original usava 9, então mantive 9. 8 também é comum)
        if i <= n - 9:
            points = data[i:i+9]
            # Verifica se todos estão acima ou todos abaixo
            # Pontos exatamente na linha central quebram a sequência
            all_pos = all(p > center_line for p in points)
            all_neg = all(p < center_line for p in points)
            
            if all_pos:
                violations.append(f"Regra 4: 9 pontos consecutivos (amostras {i+1} a {i+9}) estão acima da linha central.")
            if all_neg:
                 violations.append(f"Regra 4: 9 pontos consecutivos (amostras {i+1} a {i+9}) estão abaixo da linha central.")

    if not violations:
        violations.append("Nenhuma violação das regras de Western Electric (1-4) detectada.")
        
    # Retorna uma lista de violações únicas para não poluir o resultado
    return sorted(list(set(violations)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_cep_results')
def get_cep_results():
    try:
        results = solve_cep_problems()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)