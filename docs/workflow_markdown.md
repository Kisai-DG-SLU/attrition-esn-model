
### 1. Workflow de travail

1.  **Édition :** Tu ouvres ton fichier : `vim presentation.md`
2.  **Automation :** Dans un autre onglet de terminal, tu lances :
    ```bash
    make watch
    ```
3.  **Visualisation :** Ouvre le fichier PDF généré (`open presentation.pdf`).

À chaque  `:w` dans Vim, Marp détecte le changement et met à jour le PDF en arrière-plan quasi instantanément.

### 2. Petite astuce pour les diagrammes Mermaid

Dans le fichier Markdown, il y a des blocs `<div class="mermaid">`. Marp gère le HTML, mais pour que les diagrammes s'affichent correctement en PDF, il faut parfois s'assurer que le script Mermaid est chargé.

Si jamais les diagrammes ne s'affichent pas dans le PDF, il faut remplacer les blocs `div` par des blocs de code markdown standards comme ceci dans le fichier `.md` :

```markdown
    ```mermaid
    graph LR
    A[Start] --> B[End]
