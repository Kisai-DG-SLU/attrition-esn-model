CREATE TABLE IF NOT EXISTS "raw" (
"id_employee" INTEGER,
  "age" INTEGER,
  "revenu_mensuel" INTEGER,
  "nombre_experiences_precedentes" INTEGER,
  "annee_experience_totale" INTEGER,
  "annees_dans_l_entreprise" INTEGER,
  "annees_dans_le_poste_actuel" INTEGER,
  "satisfaction_employee_environnement" INTEGER,
  "note_evaluation_actuelle" INTEGER,
  "note_evaluation_precedente" INTEGER,
  "niveau_hierarchique_poste" INTEGER,
  "satisfaction_employee_nature_travail" INTEGER,
  "satisfaction_employee_equipe" INTEGER,
  "satisfaction_employee_equilibre_pro_perso" INTEGER,
  "nombre_participation_pee" INTEGER,
  "nb_formations_suivies" INTEGER,
  "distance_domicile_travail" INTEGER,
  "niveau_education" INTEGER,
  "annees_depuis_la_derniere_promotion" INTEGER,
  "annes_sous_responsable_actuel" INTEGER,
  "augmentation_salaire_precedente" INTEGER,
  "score_evolution_carriere" REAL,
  "indice_evolution_salaire" REAL,
  "frequence_deplacement" TEXT,
  "salaire_cat" TEXT,
  "salaire_cat_eq" TEXT,
  "position_salaire_poste" TEXT,
  "position_salaire_poste_anc" TEXT,
  "score_carriere_cat" TEXT,
  "indice_evol_cat" TEXT,
  "statut_marital" TEXT,
  "domaine_etude" TEXT,
  "poste_departement" TEXT,
  "genre" TEXT,
  "heure_supplementaires" TEXT,
  "nouveau_responsable" TEXT,
  "attrition_num" INTEGER
);
CREATE TABLE IF NOT EXISTS "model_input" (
"input_id" INTEGER,
  "timestamp" TIMESTAMP,
  "payload" TEXT
);
CREATE TABLE IF NOT EXISTS "model_output" (
"output_id" INTEGER,
  "input_id" INTEGER,
  "timestamp" TIMESTAMP,
  "prediction" TEXT,
  "model_version" TEXT
);
CREATE TABLE IF NOT EXISTS "api_log" (
"log_id" INTEGER,
  "timestamp" TIMESTAMP,
  "event_type" TEXT,
  "request_payload" TEXT,
  "response_payload" TEXT,
  "http_code" INTEGER,
  "user_id" TEXT,
  "duration_ms" INTEGER,
  "error_detail" TEXT
);
