# Makefile pour la soutenance P5
# Auteur : Damien Guesdon

MD_FILE = presentation.md
PDF_FILE = presentation.pdf
HTML_FILE = presentation.html

# Commande par défaut (génère le PDF)
all: pdf

# Générer le PDF (Haute qualité pour la présentation)
pdf:
	marp $(MD_FILE) --pdf --allow-local-files -o $(PDF_FILE)
	@echo "✅ PDF généré : $(PDF_FILE)"

# Générer le HTML (Utile pour voir les notes orateur en mode présentateur)
html:
	marp $(MD_FILE) --html --allow-local-files -o $(HTML_FILE)
	@echo "✅ HTML généré : $(HTML_FILE)"

# Mode "Watch" : Recompile automatiquement à chaque :w dans Vim
watch:
	marp $(MD_FILE) --pdf --watch --allow-local-files

# Nettoyage
clean:
	rm -f $(PDF_FILE) $(HTML_FILE)
	@echo "🧹 Fichiers générés supprimés."
```

