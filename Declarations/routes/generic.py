# Import des librairies
from flask import render_template, request, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
# l'import de func permet d'utiliser la fonction lower() dans les requêtes cette dernière est utile pour faire
# apparaître des index dans l'ordre alphabétique sans tenir compte des majuscules et minuscules alors que python est
# sensible à la casse
from sqlalchemy import func

# Import de l'application, de la base de données et du login
from ..app import app, db, login
# Import des modèles de la base de données
from ..modeles.donnees import ProcesVerbal, Theatre, Source, Personne, SalleTheatre, Adresse, Objet
from ..modeles.utilisateurs import User

# Import de la constante pour la pagination
from ..constantes import RESULTATS_PAR_PAGE


# mise en place de la route pour la page d'accueil
@app.route("/")
def accueil():
    proces_verbaux = ProcesVerbal.query.all()
    return render_template("pages/accueil.html", nom="Accueil", proces_verbaux=proces_verbaux)


# page à afficher en cas d'URL inexistante
@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', nom="Page non trouvée")


# Route qui liste les procès-verbaux dans l'ordre chronologique avec 10 résultats par page
@app.route("/proces_verbaux")
def proces_verbaux_liste():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    proces_verbaux = ProcesVerbal.query.filter(ProcesVerbal.date_pv).order_by(ProcesVerbal.date_pv.asc())\
        .paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    return render_template("pages/proces_verbaux.html", nom="Procès-verbaux", proces_verbaux=proces_verbaux)


# on crée une route vers les pages individuelles des procès-verbaux
@app.route("/proces_verbaux/<int:id>")
def proces_verbal(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id du procès-verbal
    :return: render_template
    """
    proces_verbal = ProcesVerbal.query.get_or_404(id)
    source = proces_verbal.sources
    victime = proces_verbal.victimes
    commissaire = proces_verbal.commissaires
    institution_theatre = proces_verbal.salles_theatre
    salle = institution_theatre.salles_theatre
    objet = proces_verbal.objets

    return render_template("pages/proces_verbal.html", nom="Procès-verbal", proces_verbal=proces_verbal,
                           source=source, victime=victime,
                           commissaire=commissaire, institution=institution_theatre,
                           theatre=salle, objet=objet)


# on crée un index des institutions théâtrales
@app.route("/theatres")
def theatre_liste():
    theatres = Theatre.query.all()
    return render_template("pages/theatres.html", nom="Théâtres", theatres=theatres)


# on crée une route vers les pages individuelles des institutions théâtrales
@app.route("/theatres/<int:id>")
def theatre(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id de l'institution théâtrale
    :return: render_template
    """
    theatre = Theatre.query.get_or_404(id)
    salles = theatre.salles_theatre
    proces_verbaux = theatre.proces_verbaux
    return render_template("pages/theatre.html", nom="Théâtre", theatre=theatre, salles=salles,
                           proces_verbaux=proces_verbaux)


# on crée une route vers les pages individuelles des salles de théâtre
@app.route("/salles/<int:id>")
def salle_theatre(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id de la salle de théâtre
    :return: render_template
    """
    salle = SalleTheatre.query.get_or_404(id)
    institution = salle.theatres
    proces_verbaux = ProcesVerbal.query.all()
    return render_template("pages/salle.html", nom="Salle de théâtre", salle=salle, proces_verbaux=proces_verbaux,
                           institution=institution)


# on crée un index des personnes, par ordre alphabétique de nom
@app.route("/personnes")
def personnes_liste():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    personnes = Personne.query.order_by(func.lower(Personne.nom)).paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    return render_template("pages/personnes.html", nom="Personnes", personnes=personnes)


# on crée une route vers les pages individuelles des personnes
@app.route("/personnes/<int:id>")
def personne(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id de l'individu
    :return: render_template
    """
    personne = Personne.query.get_or_404(id)
    adresses = personne.adresses
    proces_verbaux = (personne.proces_verbaux_commissaires or personne.proces_verbaux_victimes)
    return render_template("pages/personne.html", nom="Personne", personne=personne,
                            adresses=adresses, proces_verbaux=proces_verbaux)


# on crée un index des commissaires de police, par ordre alphabétique
@app.route("/commissaires")
def commissaires_liste():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    commissaires = Personne.query.filter(Personne.qualite == 'commissaire de police').order_by(Personne.nom.asc())\
        .paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    return render_template("pages/commissaires.html", nom="Commissaires", commissaires=commissaires)


# on crée un index des types d'objets volés
@app.route("/objets_voles")
def objets_voles_liste():
    objets = Objet.query.all()
    proces_verbaux = ProcesVerbal.query.order_by(ProcesVerbal.date_pv).all()
    return render_template("pages/objets_voles.html", nom="Objets volés", objets=objets,
                           proces_verbaux=proces_verbaux)


# on crée une route vers les pages individuelles des objets
@app.route("/objets_voles/<int:id>")
def objet_vole_type(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id de l'objet
    :return: render_template
    """
    objet = Objet.query.get_or_404(id)
    proces_verbaux = ProcesVerbal.query.order_by(ProcesVerbal.date_pv).all()
    return render_template("pages/objet_vole_type.html", nom="Objet volé", objet=objet,
                            proces_verbaux=proces_verbaux)


# on crée une route pour faire un index des cotes
@app.route("/sources")
def sources_liste():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    sources = Source.query.order_by(Source.cote.asc()).paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    return render_template("pages/sources.html", nom="Sources", sources=sources)


# on crée une route vers la page individuelle d'une source
@app.route("/sources/<int:id>")
def source(id):
    """
    Fonction qui permet de générer la page html pour chaque id enregistré
    :param id: id de la cote
    :return: render_template
    """
    source = Source.query.get_or_404(id)
    proces_verbaux = ProcesVerbal.query.all()
    return render_template("pages/source.html", nom="Source", source=source, proces_verbaux=proces_verbaux)


# on crée une route pour faire un index des noms de rue enregistrés
@app.route("/adresses")
def adresses_liste():
    page = request.args.get("page", 1)
    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    # on affiche les rues dans l'ordre alphabétique sans tenir compte de la casse grâce à func.lower()
    adresses = Adresse.query.order_by(func.lower(Adresse.rue).asc()).paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    return render_template("pages/adresses.html", nom="Adresses", adresses=adresses)


# On définit les requêtes pour le formulaire de recherche
# on utilise la méthode .like() pour permettre une recherche plus large à partir de la chaine de caractères envoyée
@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    # on crée une liste vide pour y ajouter les résultats
    resultats = []
    titre = "Recherche"
    if motclef:
        # pour chercher les procès-verbaux enregistrés, par date
        items = ProcesVerbal.query.filter(
            ProcesVerbal.date_pv.like("%{}%".format(motclef))
        ).all()
        # pour chaque résultat, on l'ajoute dans la liste resultats
        for item in items:
            resultats.append([item.date_pv, url_for('proces_verbal', id=item.id)])

        # pour chercher les institutions théâtrales enregistrées
        items = Theatre.query.filter(
            Theatre.institution.like("%{}%".format(motclef))
        ).all()
        for item in items:
            resultats.append([item.institution, url_for('theatre', id=item.id)])

        # pour chercher les salles de théâtres enregistrées
        items = SalleTheatre.query.filter(
            SalleTheatre.nom_salle.like("%{}%".format(motclef))
        ).all()
        for item in items:
            resultats.append([item.nom_salle, url_for('salle_theatre', id=item.id)])

        # pour chercher les types d'objets enregistrés
        items = Objet.query.filter(
            Objet.type.like("%{}%".format(motclef))
        ).all()
        for item in items:
            resultats.append([item.type, url_for('objet_vole_type', id=item.id)])

        # pour chercher les commissaires enregistrés, par nom de famille
        items = Personne.query.filter(db.or_(Personne.nom.like("%{}%".format(motclef)),
                                              Personne.prenom.like("%{}%".format(motclef)))).all()
        for item in items:
            resultats.append([item.prenom + " " + item.nom, url_for('personne', id=item.id)])

        titre = "Résultat pour la recherche '" + motclef + "'"
    return render_template("pages/recherche.html", resultats=resultats, titre=titre)


# Route pour le formulaire d'inscription
# Le succès et les erreurs sont gérés avec flash
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


# Route pour permettre la connexion de l'utilisateur
# On vérifie d'abord que l'utilisateur n'est pas déjà connecté, il en est informé avec flash
# Quand le formulaire est envoyé, flash informe du succès ou des erreurs survenues
# Si la connexion est effectuée, l'utilisateur est renvoyé vers la page d'accueil
@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Vous êtes à présent connecté-e", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")


login.login_view = 'connexion'


# Route pour permettre la déconnexion
@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")


# routes pour les formulaires d'ajout dans la base de données, depuis un compte enregistré
# Quand le formulaire est envoyé, flash informe du succès et redirige vers l'accueil ou informe de l'erreur
@app.route("/ajout_source", methods=["GET", "POST"])
@login_required
def ajout_source():
    # Ajout d'une référence archivistique
    # on récupère les données à enregistrer dans la base
    if request.method == "POST":
        statut, informations = Source.ajout_source(
            ajout_source_cote=request.form.get("ajout_source_cote", None)
        )

        # on informe du succès et on redirige vers la page d'accueil
        if statut is True:
            flash("Ajout d'une nouvelle source", "success")
            return redirect("/")
        # sinon, on informe des erreurs et on reste sur la page
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_source.html", nom="Ajouter une source")
    else:
        return render_template("pages/ajout/ajout_source.html", nom="Ajouter une source")


@app.route("/ajout_objet", methods=["GET", "POST"])
@login_required
def ajout_objet():
    # Ajout d'un objet
    if request.method == "POST":
        statut, informations = Objet.ajout_objet(
            ajout_objet_type=request.form.get("ajout_objet_type", None)
        )

        if statut is True:
            flash("Ajout d'un nouvel objet", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_objet.html", nom="Ajouter un objet")
    else:
        return render_template("pages/ajout/ajout_objet.html", nom="Ajouter un objet")


@app.route("/ajout_personne", methods=["GET", "POST"])
@login_required
def ajout_personne():
    # Ajout d'une personne
    if request.method == "POST":
        statut, informations = Personne.ajout_personne(
            ajout_personne_nom=request.form.get("ajout_personne_nom", None),
            ajout_personne_prenom=request.form.get("ajout_personne_prenom", None),
            ajout_personne_qualite=request.form.get("ajout_personne_qualite", None)
        )

        if statut is True:
            flash("Ajout d'une nouvelle personne", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_personne.html", nom="Ajouter une personne")
    else:
        return render_template("pages/ajout/ajout_personne.html", nom="Ajouter une personne")


@app.route("/ajout_adresse", methods=["GET", "POST"])
@login_required
def ajout_adresse():
    # Ajout d'une adresse
    if request.method == "POST":
        statut, informations = Adresse.ajout_adresse(
            ajout_adresse_rue=request.form.get("ajout_adresse_rue", None),
            ajout_adresse_quartier=request.form.get("ajout_adresse_quartier", None))

        if statut is True:
            flash("Ajout d'une nouvelle adresse. Vous pouvez à présent la lier à une personne en vous rendant sur la "
                  "page de la personne et en cliquant sur le bouton pour modifier les informations.", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_adresse.html", nom="Ajouter une adresse")
    else:
        return render_template("pages/ajout/ajout_adresse.html", nom="Ajouter une adresse")


# route pour créer un lien entre un individu de Personne et une adresse de Adresse
@app.route("/personnes/<int:id>/adresse", methods=["GET", "POST"])
@login_required
def lien_adresse_personne(id):
    personne = Personne.query.get(id)
    adresses = Adresse.query.all()
    if request.method == "GET":
        return render_template("pages/ajout/ajout_domicile.html", nom="Ajouter un domicile", personne=personne,
                               adresses=adresses)

    if request.method == "POST":
        statut, informations = Personne.lier_personne_adresse(id=id,
                                                              adresse_id=request.form.get("adresse_id", None))

        if statut is True:
            flash("Ajout d'un domicile pour l'individu enregistré", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_domicile.html", nom="Ajouter un domicile", personne=personne,
                                   adresses=adresses)

    else:
        return render_template("pages/ajout/ajout_domicile.html", nom="Ajouter un domicile",  personne=personne,
                               adresses=adresses)


@app.route("/ajout_proces_verbal", methods=["GET", "POST"])
@login_required
def ajout_proces_verbal():
    # Ajout d'un procès-verbal
    sources = Source.query.all()
    theatres = Theatre.query.all()
    commissaires = Personne.query.filter(Personne.qualite == 'commissaire de police').all()
    victimes = Personne.query.filter(Personne.qualite != 'commissaire de police').all()
    objets = Objet.query.all()

    if request.method == "POST":
        statut, informations = ProcesVerbal.ajout_proces_verbal(
            ajout_proces_verbal_date=request.form.get("ajout_proces_verbal_date", None),
            ajout_pv_id_source=request.form.get("ajout_pv_id_source", None),
            ajout_pv_id_theatre=request.form.get("ajout_pv_id_theatre", None),
            ajout_pv_id_commissaire=request.form.get("ajout_pv_id_commissaire", None),
            ajout_pv_id_victime=request.form.get("ajout_pv_id_victime", None),
            ajout_pv_id_objet=request.form.get("ajout_pv_id_objet", None),

        )

        if statut is True:
            flash("Ajout d'un nouveau procès-verbal", "success")
            return redirect("/")
        else:
            flash("L'ajout a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/ajout/ajout_proces_verbal.html", nom="Ajouter un procès-verbal", sources=sources,
                                   theatres=theatres, commissaires=commissaires, victimes=victimes, objets=objets)
    else:
        return render_template("pages/ajout/ajout_proces_verbal.html", nom="Ajouter un procès-verbal", sources=sources,
                               theatres=theatres, commissaires=commissaires, victimes=victimes, objets=objets)


# routes pour permettre les modifications dans les enregistrements de la base de données
# chaque fonction prend comme paramètre l'id de l'élément à modifier
@app.route("/proces_verbaux/<int:id>/update", methods=["GET", "POST"])
@login_required
def modification_proces_verbal(id):
    update_proces_verbal = ProcesVerbal.query.get_or_404(id)
    proces_verbaux_dates = ProcesVerbal.query.filter(ProcesVerbal.date_pv).all()
    sources = Source.query.all()
    theatres = Theatre.query.all()
    commissaires = Personne.query.filter(Personne.qualite == 'commissaire de police').all()
    victimes = Personne.query.filter(Personne.qualite != 'commissaire de police').all()
    objets = Objet.query.all()

    if request.method == "GET":
        return render_template("pages/modification/update_proces_verbal.html", nom="Modifier un procès-verbal",
                               proces_verbal=update_proces_verbal, sources=sources, theatres=theatres,
                               dates=proces_verbaux_dates, commissaires=commissaires, victimes=victimes, objets=objets)
    else:
        statut, informations = ProcesVerbal.modification_proces_verbal(
            id=id,
            update_date=request.form.get("date_pv", None),
            update_id_source=request.form.get("id_source", None),
            update_id_theatre=request.form.get("id_theatre", None),
            update_id_commissaire=request.form.get("id_commissaire", None),
            update_id_victime=request.form.get("id_victime", None),
            update_id_objet=request.form.get("id_objet", None)
            )

        if statut is True:
            flash("Modification du procès-verbal enregistré", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/modification/update_proces_verbal.html", nom="Modifier un procès-verbal",
                                   proces_verbal=update_proces_verbal,sources=sources, theatres=theatres,
                                   dates=proces_verbaux_dates, commissaires=commissaires, victimes=victimes, objets=objets)


@app.route("/objets_voles/<int:id>/update", methods=["GET", "POST"])
@login_required
def modification_objet(id):
    update_objet = Objet.query.get(id)
    if request.method == "GET":
        return render_template("pages/modification/update_objet.html", nom="Modifier un objet", objet=update_objet)

    else:
        statut, informations = Objet.modification_objet(
            id=id,
            objet_type=request.form.get("type", None)
        )

        if statut is True:
            flash("Modification du type de l'objet enregistré", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/modification/update_objet.html", nom="Modifier un objet", objet=update_objet)


@app.route("/theatres/<int:id>/update", methods=["GET", "POST"])
@login_required
def modification_salle(id):
    update_salle = SalleTheatre.query.get(id)
    institutions_theatrales = Theatre.query.all()
    if request.method == "GET":
        return render_template("pages/modification/update_salle.html", nom="Modifier une salle", salle=update_salle,
                               theatres=institutions_theatrales)

    else:
        statut, informations = SalleTheatre.modification_salle(
            id=id,
            update_nom=request.form.get("update_nom", None),
            update_dates=request.form.get("update_dates", None),
            id_institution=request.form.get("id_institution", None)
        )

        if statut is True:
            flash("Modification de la salle de théâtre enregistrée", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/modification/update_salle.html", nom="Modifier un théâtre", salle=update_salle,
                                   theatres=institutions_theatrales)


@app.route("/personnes/<int:id>/update", methods=["GET", "POST"])
@login_required
def modification_personne(id):
    update_personne = Personne.query.get(id)
    if request.method == "GET":
        return render_template("pages/modification/update_personne.html", nom="Modifier une personne", personne=update_personne)

    else:
        statut, informations = Personne.modification_personne(
            id=id,
            update_nom=request.form.get("update_nom", None),
            update_prenom=request.form.get("update_prenom", None),
            update_qualite=request.form.get("update_qualite", None)
        )

        if statut is True:
            flash("Modification des informations sur la personne enregistrée", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/modification/update_personne.html", nom="Modifier une personne", personne=update_personne)


# Routes pour permettre les suppressions
# Chaque fonction prend comme paramètre l'id de l'élément à supprimer
@app.route("/objets_voles/<int:id>/delete", methods=["POST", "GET"])
@login_required
def suppression_objet(id):
    delete_objet = Objet.query.get(id)
    if request.method == "POST":
        statut = Objet.suppression_objet(id=id)

        if statut is True:
            flash("Suppression réussie.", "success")
            return redirect("/")
        else:
            flash("Échec de la suppression.", "danger")
            return redirect("/objets_voles/<int:id>")
    else:
        return render_template("pages/suppression/delete_objet.html", nom="Supprimer un objet",  objet=delete_objet)


@app.route("/personnes/<int:id>/delete", methods=["POST", "GET"])
@login_required
def suppression_personne(id):
    delete_personne = Personne.query.get(id)
    if request.method == "POST":
        statut = Personne.suppression_personne(id=id)

        if statut is True:
            flash("Suppression réussie.", "success")
            return redirect("/")
        else:
            flash("Échec de la suppression.", "danger")
            return redirect("/personnes/<int:id>")
    else:
        return render_template("pages/suppression/delete_personne.html", nom="Supprimer une personne",  personne=delete_personne)


# route pour supprimer un lien entre un individu de Personne et une adresse de Adresse
@app.route("/personnes/<int:id>/adresse/delete/<int:adresse_id>", methods=["GET", "POST"])
@login_required
def suppression_adresse_personne(id, adresse_id):
    personne = Personne.query.get(id) # on récupère l'id de la personne pour laquelle on supprime l'adresse
    adresse = Adresse.query.get(adresse_id) # on récupère l'id de l'adresse qu'on délie de la personne

    if request.method == "GET":
        return render_template("pages/suppression/delete_domicile.html", nom="Supprimer un domicile", personne=personne,
                               adresse=adresse)

    if request.method == "POST":
        statut, informations = Personne.delier_personne_adresse(id=id, adresse_id=adresse_id)

        if statut is True:
            flash("Suppression d'un domicile pour l'individu enregistrée", "success")
            return redirect("/")
        else:
            flash("La modification a échoué pour les raisons suivantes : " + ", ".join(informations), "danger")
            return render_template("pages/suppression/delete_domicile.html", nom="Supprimer un domicile", personne=personne,
                                   adresse=adresse)

    else:
        return render_template("pages/suppression/delete_domicile.html", nom="Ajouter un domicile",  personne=personne,
                               adresse=adresse)


@app.route("/adresses/<int:id>/delete", methods=["POST", "GET"])
@login_required
def suppression_adresse(id):
    delete_adresse = Adresse.query.get(id)
    if request.method == "POST":
        statut = Adresse.suppression_adresse(id=id)

        if statut is True:
            flash("Suppression réussie.", "success")
            return redirect("/")
        else:
            flash("Échec de la suppression.", "danger")
            return redirect("/")
    else:
        return render_template("pages/suppression/delete_adresse.html", nom="Supprimer une adresse",  adresse=delete_adresse)


@app.route("/proces_verbaux/<int:id>/delete", methods=["POST", "GET"])
@login_required
def suppression_proces_verbal(id):
    delete_proces_verbal = ProcesVerbal.query.get(id)
    if request.method == "POST":
        statut = ProcesVerbal.suppression_proces_verbal(id=id)

        if statut is True:
            flash("Suppression réussie.", "success")
            return redirect("/")
        else:
            flash("Échec de la suppression.", "danger")
            return redirect("/proces_verbaux/<int:id>")
    else:
        return render_template("pages/suppression/delete_proces_verbal.html", nom="Supprimer un procès-verbal",
                               proces_verbal=delete_proces_verbal)


@app.route("/sources/<int:id>/delete", methods=["POST", "GET"])
@login_required
def suppression_source(id):
    delete_source = Source.query.get(id)
    if request.method == "POST":
        statut = Source.suppression_source(id=id)

        if statut is True:
            flash("Suppression réussie.", "success")
            return redirect("/")
        else:
            flash("Échec de la suppression.", "danger")
            return redirect("/sources/<int:id>")
    else:
        return render_template("pages/suppression/delete_source.html", nom="Supprimer une source",  source=delete_source)


# route qui gère la page avec la carte de localisation des théâtres
@app.route("/carte")
def carte():
    localisation_salles = SalleTheatre.query.all()
    return render_template('pages/carte.html', nom="Carte des théâtres", salles=localisation_salles)
