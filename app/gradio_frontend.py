import gradio as gr
import requests
import base64
import io
from PIL import Image
import pandas as pd

FASTAPI_URL = "http://localhost:8000/predict/"
EMPLOYEE_LIST_URL = "http://localhost:8000/employee_list"
HEALTH_URL = "http://localhost:8000/health"

# Initialisation de la liste à vide
all_ids = []


def fetch_id_list():
    try:
        resp = requests.get(EMPLOYEE_LIST_URL, timeout=5)
        if resp.status_code == 200:
            ids = [str(i) for i in resp.json() if str(i).isdigit()]
            return ids
    except Exception as e:
        print(f"Erreur récupération liste employés : {e}")
    return []


def format_pred_string(pred):
    if pred == "OUI":
        return "<span style='color:red; font-weight:bold; font-size: 1.2em;'>🔴 OUI</span> (risque de départ probable)"
    elif pred == "NON":
        return "<span style='color:green; font-weight:bold; font-size: 1.2em;'>🟢 NON</span> (risque de départ peu probable)"
    return f"{pred}"


def match_and_sum_shap(raw_features, shap_contribs):
    SPECIALS = {
        "salaire_cat",
        "salaire_cat_eq",
        "position_salaire_poste",
        "position_salaire_poste_anc",
    }
    lines = []
    for base_feat, raw_val in raw_features.items():
        shap_sum = 0.0
        for sk, v in shap_contribs.items():
            sk_clean = sk.split("__", 1)[-1] if "__" in sk else sk
            if base_feat in SPECIALS:
                if sk_clean == base_feat:
                    try:
                        shap_sum += float(v)
                    except (ValueError, TypeError):
                        continue
            else:
                if sk_clean.startswith(base_feat):
                    try:
                        shap_sum += float(v)
                    except (ValueError, TypeError):
                        continue
        if shap_sum > 0.001:
            exp = "⚠️"
        elif shap_sum < -0.001:
            exp = "✅"
        else:
            exp = "-"
        lines.append([base_feat, raw_val, exp])
    return pd.DataFrame(lines, columns=["Variable", "Valeur brute", "Explicabilité"])


def filter_ids(search):
    global all_ids
    search = search.lower().strip()
    filtered = (
        [i for i in all_ids if search in i.lower()] if all_ids and search else all_ids
    )
    return [[i] for i in filtered[:30]] if filtered else [["API hors service"]]


def predict_attrition(manual_id):
    try:
        id_employee = int(str(manual_id).strip())
    except Exception as e:
        return (
            format_pred_string(f"Erreur ID sélectionné : {e}"),
            "-",
            None,
            pd.DataFrame(),
        )
    try:
        resp = requests.get(
            FASTAPI_URL, params={"id_employee": id_employee}, timeout=12
        )
        if resp.status_code != 200:
            return (
                format_pred_string(f"Erreur API statut {resp.status_code}"),
                "-",
                None,
                pd.DataFrame(),
            )
        res = resp.json()
    except Exception as e:
        return (
            format_pred_string(f"Erreur d'appel API : {e}"),
            "-",
            None,
            pd.DataFrame(),
        )
    if res.get("error"):
        msg = f"<span style='color:red; font-weight:bold;'>⚠️ {res['error']}</span>"
        return msg, "-", None, pd.DataFrame()
    pred_raw = res.get("prediction", "Erreur")
    pred = format_pred_string(pred_raw)
    score = res.get("score", "N/A")
    raw_features = res.get("donnees_brutes", {})
    shap_contribs = res.get("shap_waterfall", {})
    table = match_and_sum_shap(raw_features, shap_contribs)
    img_b64 = res.get("shap_waterfall_img", None)
    img = None
    if img_b64:
        try:
            img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
        except Exception:
            img = None
    return pred, score, img, table


def check_health():
    global all_ids
    try:
        resp = requests.get(HEALTH_URL, timeout=3)
        if resp.status_code == 200 and resp.json().get("status") == "ok":
            version = resp.json().get("version", "?")
            banner = f"<span style='color:green; font-weight:bold;'>🟢 API FastAPI opérationnelle (version {version})</span>"
            interactive = True
            all_ids = fetch_id_list()  # refresh la liste quand API UP
        else:
            banner = "<span style='color:red; font-weight:bold;'>🔴 API FastAPI hors service !</span>"
            interactive = False
            all_ids = []
    except Exception:
        banner = "<span style='color:red; font-weight:bold;'>🔴 API FastAPI hors service !</span>"
        interactive = False
        all_ids = []
    df_value = [[i] for i in all_ids[:30]] if all_ids else [["API hors service"]]
    return (
        banner,
        gr.Textbox(
            interactive=interactive,
            label="Filtrer la liste d'IDs salariés",
            placeholder="Ex: 14",
        ),
        gr.Dataframe(
            value=df_value,
            headers=["id_employee"],
            label="Liste filtrée (30 max)",
            interactive=False,
        ),
        gr.Textbox(
            interactive=interactive,
            label="ID à prédire (copier/coller depuis la table)",
            placeholder="Ex: 1427",
        ),
        gr.Button(interactive=interactive, value="Prédire"),
    )


with gr.Blocks() as demo:
    health_banner = gr.HTML("Cliquez sur le bouton pour vérifier l'état de l'API.")
    refresh_btn = gr.Button("Vérifier l'état de l'API")
    gr.Markdown("## Risque d'attrition ESN - Demo API FastAPI + Gradio")
    with gr.Row():
        search_box = gr.Textbox(
            label="Filtrer la liste d'IDs salariés",
            placeholder="Ex: 14",
            interactive=True,
        )
        id_table = gr.Dataframe(
            value=[["API hors service"]],
            headers=["id_employee"],
            label="Liste filtrée (30 max)",
            interactive=False,
        )
    with gr.Row():
        id_textbox = gr.Textbox(
            label="ID à prédire (copier/coller depuis la table)",
            placeholder="Ex: 1427",
            interactive=True,
        )
        pred_btn = gr.Button("Prédire", interactive=True)
    with gr.Row():
        pred_out = gr.HTML(label="Prédiction (OUI/NON)")
        score_out = gr.Textbox(label="Score du modèle")
    with gr.Row():
        img_out = gr.Image(label="Graphique SHAP waterfall", type="pil")
        table_out = gr.Dataframe(label="Données brutes et Explicabilité", wrap=True)

    def update_table(search):
        return filter_ids(search)

    search_box.change(update_table, inputs=search_box, outputs=id_table)
    pred_btn.click(
        fn=predict_attrition,
        inputs=[id_textbox],
        outputs=[pred_out, score_out, img_out, table_out],
    )
    refresh_btn.click(
        check_health,
        inputs=[],
        outputs=[health_banner, search_box, id_table, id_textbox, pred_btn],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
