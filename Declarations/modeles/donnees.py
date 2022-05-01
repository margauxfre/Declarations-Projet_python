# on importe la base de données pour accéder aux données et établir les modèles
from ..app import db

# Import qui permet d'enregistrer dans la table Authorship l'utilisateur courant qui fait
# des modifications dans la base de données
from flask_login import current_user

# permet d'enregistrer le moment précis où un utilisateur modifie la base de données depuis l'application
import datetime


# par une table de relation, on lie les individus aux adresses : on crée une relation many-to-many puisqu'un individu
# peut être enregistré à plusieurs adresses et inversement. On définit le nom de la table de relation et les deux
# colonnes qu'elle contient, elles référencent chacune une clé étrangère. Les deux tables contentant les adresses et les
# personnes sont définies dans les 'class' ci-dessous. Si une adresse ou un individu est supprimé, la relation l'est
# également automatiquement
Habite = db.Table("habite", db.Column("id", db.Integer, nullable=False, autoincrement=True, primary_key=True),
                  db.Column("id_personne", db.Integer, db.ForeignKey("personne.id", onupdate="CASCADE",
                                                                     ondelete="CASCADE"), primary_key=True),
                  db.Column("id_adresse", db.Integer, db.ForeignKey("adresse.id", onupdate="CASCADE",
                                                                    ondelete="CASCADE"), primary_key=True))


# on définit les classes, chacune correspondant à une table de la BDD
class Personne(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    prenom = db.Column(db.Text)
    qualite = db.Column(db.Text)
    # .relationship() permet de définir des liens entre les tables, notamment par le référencement en clé étrangère
    proces_verbaux_commissaires = db.relationship("ProcesVerbal", back_populates="commissaires",
                                                  foreign_keys="ProcesVerbal.id_commissaire")
    proces_verbaux_victimes = db.relationship("ProcesVerbal", back_populates="victimes",
                                              foreign_keys="ProcesVerbal.id_victime")
    # le paramètre secondary renvoie à la table de relation définie ci-dessus, il permet d'enregistrer chaque relation
    # entre une personne et une adresse dans la table de relation automatiquement, le même paramètre est présent pour la
    # variable 'personnes' de la class Adresse
    adresses = db.relationship("Adresse", secondary=Habite, back_populates="personnes")
    authorships = db.relationship("Authorship", back_populates="personne")

    # fonction qui permet d'ajouter une nouvelle entrée dans la table
    @staticmethod
    def ajout_personne(ajout_personne_nom, ajout_personne_prenom, ajout_personne_qualite):
        """
        Fonction qui permet d'ajouter une nouvelle personne à la base de données
        :param ajout_personne_nom: nom de la personne
        :param ajout_personne_prenom: prénom de la personne
        :param ajout_personne_qualite : qualité/métier de la personne
        :returns: tuple (booléen, liste/objet)
        """
        # on définit une liste vide pour les erreurs
        erreurs = []
        # on définit des erreurs
        if not ajout_personne_nom:
            erreurs.append(
                "Veuillez renseigner le nom de la personne.")
        if not ajout_personne_prenom:
            erreurs.append(
                "Veuillez renseigner le prénom de la personne.")
        if (ajout_personne_nom and ajout_personne_prenom) and not (
                ajout_personne_nom[0].isupper() and ajout_personne_prenom[0].isupper()):
            erreurs.append(
                "Le nom et le prénom de la personne doivent commencer par une majuscule.")

        # on définit une variable qui contient les informations pour la nouvelle personne à enregistrer
        # chaque champ correspond à un paramètre du modèle
        nouvelle_personne = Personne.query.filter(db.and_(Personne.nom == ajout_personne_nom,
                                                          Personne.prenom == ajout_personne_prenom,
                                                          Personne.qualite == ajout_personne_qualite)).count()

        # on vérifie que la personne n'est pas déjà enregistrée
        if nouvelle_personne > 0:
            erreurs.append("Cette personne existe déjà dans la base de données.")

        # on vérifie s'il y a une erreur et on retourne l'erreur s'il y en a une
        if len(erreurs) > 0:
            return False, erreurs

        # s'il n'y a pas d'erreur, on ajoute la nouvelle entrée dans la table Personne
        # chaque champ correpond aux paramètres du modèle
        nouvelle_personne = Personne(nom=ajout_personne_nom,
                                     prenom=ajout_personne_prenom,
                                     qualite=ajout_personne_qualite)

        # on lance l'ajout dans la BDD, ce dernier sera stoppé s'il y a une erreur
        try:
            db.session.add(nouvelle_personne)
            db.session.commit()
            return True, nouvelle_personne

        except Exception as erreur:
            return False, [str(erreur)]

    # fonction pour permettre la modification d'une entrée dans la table Personne
    @staticmethod
    def modification_personne(id, update_nom, update_prenom, update_qualite):
        """
               Fonction qui permet d'ajouter une nouvelle personne à la base de données
               :param id: id de la personne sur laquelle on va effectuer des modifications
               :param update_nom: nom de la personne
               :param update_prenom: prénom de la personne
               :param update_qualite : qualité/métier de la personne
               :returns: tuple (booléen, liste/objet)
               """

        # on récupère la personne pour laquelle on veut faire des modifications
        update_personne = Personne.query.get_or_404(id)
        erreurs = []

        if not update_nom:
            erreurs.append("Veuillez renseigner le nom.")
        if not update_prenom:
            erreurs.append("Veuillez renseigner le prénom.")
        if (update_nom and update_prenom) and not (
                update_nom[0].isupper() and update_prenom[0].isupper()):
            erreurs.append(
                "Le nom et le prénom de la personne doivent commencer par une majuscule.")

        # on vérifie qu'au moins un changement a été effectué
        if update_personne.nom == update_nom and update_personne.prenom == update_prenom \
                and update_personne.qualite == update_qualite:
            erreurs.append("Aucun changement n'a été effectué.")

        # on vérifie s'il y a une erreur et on retourne le message d'erreur
        if len(erreurs) > 0:
            return False, erreurs

        # on associe les modifications aux champs correspondants
        update_personne.nom = update_nom
        update_personne.prenom = update_prenom
        update_personne.qualite = update_qualite

        # on lance l'ajout dans la BDD, ce dernier sera stoppé s'il y a une erreur
        try:
            db.session.add(update_personne)
            db.session.add(Authorship(id_personne=update_personne.id, id_user=current_user.id))
            db.session.commit()
            return True, update_personne

        except Exception as erreur:
            return False, [str(erreur)]


    #fonction pour supprimer une entrée de la base, dans la table Personne
    @staticmethod
    def suppression_personne(id):
        """
        Fonction qui permet de supprimer une personne de la base de données
        :param id: id de la personne à supprimer
        """

        # on récupère la personne avec son id
        delete_personne = Personne.query.get_or_404(id)

        # On supprime la personne s'il n'y a pas d'erreur
        try:
            db.session.delete(delete_personne)
            db.session.commit()
            return True

        except Exception as erreur:
            return False, [str(erreur)]

    # fonction pour ajouter une adresse de domicile à la personne
    @staticmethod
    def lier_personne_adresse(id, adresse_id):
        """
        Fonction qui permet de créer une relation entre une adresse de domicile et un individu
        :param id: id de la personne à lier à l'adresse
        :param adresse_id: id de l'adresse à lier à la personne
        """
        erreurs = []
        personne = Personne.query.get(id) # on récupère la personne à partir de son id
        adresse = Adresse.query.get(adresse_id) # on récupère l'adresse à partir de son id

        # si la relation personne-adresse n'existe pas, on l'ajoute dans la table de relation Habite avec la méthode
        # .append()
        if adresse not in personne.adresses:
            personne.adresses.append(adresse)
        # sinon on affiche une erreur
        else:
            erreurs.append("L'adresse est déjà enregistrée pour cet individu.")
            return False, erreurs

        try:
            db.session.add(Authorship(id_adresse=adresse.id, id_personne=personne.id, id_user=current_user.id))
            db.session.commit()
            return True, ""

        except Exception as erreur:
            return False, [str(erreur)]

    # fonction pour supprimer une adresse de domicile liée à une personne
    @staticmethod
    def delier_personne_adresse(id, adresse_id):
        """
        Fonction qui permet de supprimer la relation entre une adresse de domicile et un individu
        :param id: id de la personne à lier à l'adresse
        :param adresse_id: id de l'adresse à lier à la personne
        """
        personne = Personne.query.get(id) # on récupère la personne à partir de son id
        adresse = Adresse.query.get(adresse_id) # on récupère l'adresse à partir de son id

        # on supprime la relation entre l'adresse et l'individu avec la méthode .remove()
        personne.adresses.remove(adresse)

        try:
            db.session.add(Authorship(id_adresse=adresse.id, id_personne=personne.id, id_user=current_user.id))
            db.session.commit()
            return True, ""

        except Exception as erreur:
            return False, [str(erreur)]


class Adresse(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    rue = db.Column(db.Text)
    quartier = db.Column(db.Text)
    personnes = db.relationship("Personne", secondary=Habite, back_populates='adresses')
    authorships = db.relationship("Authorship", back_populates="adresse")

    @staticmethod
    def ajout_adresse(ajout_adresse_rue, ajout_adresse_quartier):
        """
            Fonction qui permet d'ajouter une nouvelle adresse à la base de données
            :param ajout_adresse_rue: nom de la rue
            :param ajout_adresse_quartier: nom qu quartier où est située la rue
            :returns: tuple (booléen, liste/objet)
        """
        erreurs = []

        if not ajout_adresse_rue:
            erreurs.append(
                "Veuillez renseigner le nom de la rue.")

        if not ajout_adresse_quartier:
            erreurs.append(
                "Veuillez renseigner le quartier où est située la rue.")

        nouvelle_adresse = Adresse.query.filter(db.and_(Adresse.rue == ajout_adresse_rue),
                                                (Adresse.quartier == ajout_adresse_quartier)).count()

        if nouvelle_adresse > 0:
            erreurs.append("Cette adresse existe déjà dans la base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        nouvelle_adresse = Adresse(rue=ajout_adresse_rue,
                                   quartier=ajout_adresse_quartier)

        try:
            db.session.add(nouvelle_adresse)
            db.session.commit()
            return True, nouvelle_adresse

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def suppression_adresse(id):
        """
        Fonction pour supprimer une adresse
        :param id: id de l'adresse à supprimer
        """
        delete_adresse = Adresse.query.get_or_404(id)

        try:
            db.session.delete(delete_adresse)
            db.session.commit()
            return True

        except Exception as erreur:
            return False, [str(erreur)]


class Theatre(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    institution = db.Column(db.Text, nullable=False)
    salles_theatre = db.relationship("SalleTheatre", back_populates="theatres")
    proces_verbaux = db.relationship("ProcesVerbal", back_populates="salles_theatre")


class SalleTheatre(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    nom_salle = db.Column(db.Text)
    dates_occupation_salle = db.Column(db.Text)
    id_institution = db.Column(db.Integer, db.ForeignKey("theatre.id"))
    # la latitude et la longitude seront utiles pour établir une carte de localisation des salles parisiennes de la fin
    # du XVIIIe siècle
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    theatres = db.relationship("Theatre", back_populates="salles_theatre")
    authorships = db.relationship("Authorship", back_populates="salle_theatre")

    # pas de fonction d'ajout ou suppression pour les salles puisque toutes les salles sur la période sont ajoutées à
    # la BDD
    @staticmethod
    def modification_salle(id, update_nom, update_dates, id_institution):
        """
             Fonction qui permet de modifier une salle
             :param id: id de la salle sur laquelle on va effectuer des modifications
             :param update_nom: nom de la salle
             :param update_dates: dates d'occupation de la salle
             :param id_institution : identifiant de l'institution théâtrale qui occupe la salle
             :returns: tuple (booléen, liste/objet)
             """

        update_salle = SalleTheatre.query.get_or_404(id)
        erreurs = []

        if not update_nom:
            erreurs.append("Veuillez renseigner le nom de la salle.")
        if not update_dates:
            erreurs.append("Veuillez renseigner les dates d'occupation.")
        if update_salle.nom_salle == update_nom and update_salle.dates_occupation_salle == update_dates \
                and update_salle.id_institution == id_institution:
            erreurs.append("Aucun changement n'a été effectué.")

        if len(erreurs) > 0:
            return False, erreurs

        update_salle.nom_salle = update_nom
        update_salle.dates_occupation_salle = update_dates
        update_salle.id_institution = id_institution

        try:
            db.session.add(update_salle)
            db.session.add(Authorship(id_salle_theatre=update_salle.id, id_user=current_user.id))
            db.session.commit()
            return True, update_salle

        except Exception as erreur:
            return False, [str(erreur)]


class ProcesVerbal(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    date_pv = db.Column(db.String(10))
    id_theatre = db.Column(db.Integer, db.ForeignKey("theatre.id"))
    id_source = db.Column(db.Integer, db.ForeignKey("source.id"))
    id_commissaire = db.Column(db.Integer, db.ForeignKey("personne.id"))
    id_victime = db.Column(db.Integer, db.ForeignKey("personne.id"))
    id_objet = db.Column(db.Integer, db.ForeignKey("objet.id"))
    commissaires = db.relationship("Personne", back_populates="proces_verbaux_commissaires",
                                   foreign_keys=id_commissaire)
    victimes = db.relationship("Personne", back_populates="proces_verbaux_victimes", foreign_keys=id_victime)
    salles_theatre = db.relationship("Theatre", back_populates="proces_verbaux")
    sources = db.relationship("Source", back_populates="proces_verbaux_sources")
    objets = db.relationship("Objet", back_populates="proces_verbaux_objets")
    authorships = db.relationship("Authorship", back_populates="proces_verbal")

    @staticmethod
    def ajout_proces_verbal(ajout_proces_verbal_date, ajout_pv_id_theatre, ajout_pv_id_source, ajout_pv_id_commissaire,
                            ajout_pv_id_victime, ajout_pv_id_objet):
        """
        Fonction pour ajouter un procès-verbal à la base de données
        :param ajout_proces_verbal_date: date de rédaction du document
        :param ajout_pv_id_theatre: identifiant du théâtre où s'est déroulé le vol
        :param ajout_pv_id_source: id de la la cote du document
        :param ajout_pv_id_commissaire: id du commissaire ayant traité l'affaire
        :param ajout_pv_id_victime: id de la victime du vol
        :param ajout_pv_id_objet: id de l'objet convoité
        """
        erreurs = []
        if not ajout_proces_verbal_date:
            erreurs.append(
                "Veuillez renseigner la date du procès-verbal à enregistrer.")
        if not len(ajout_proces_verbal_date) == 10:
            erreurs.append("La cote doit prendre la forme suivante : AAAA-MM-JJ, ex :\"1784-04-06\" (10 caractères).")
        if not (ajout_proces_verbal_date.startswith('177') or ajout_proces_verbal_date.startswith('178')):
            erreurs.append(
                "Veuillez renseigner une date valide (entre 1770 et 1789).")

        nouveau_proces_verbal = Source.query.filter(
            ProcesVerbal.date_pv == ajout_proces_verbal_date,
            ProcesVerbal.id_theatre == ajout_pv_id_theatre,
            ProcesVerbal.id_source == ajout_pv_id_source,
            ProcesVerbal.id_commissaire == ajout_pv_id_commissaire,
            ProcesVerbal.id_victime == ajout_pv_id_victime,
            ProcesVerbal.id_objet == ajout_pv_id_objet
        ).count()
        if nouveau_proces_verbal > 0:
            erreurs.append("Ce procès-verbal existe déjà dans la base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        nouveau_proces_verbal = ProcesVerbal(date_pv=ajout_proces_verbal_date,
                                             id_theatre=ajout_pv_id_theatre,
                                             id_source=ajout_pv_id_source,
                                             id_commissaire=ajout_pv_id_commissaire,
                                             id_victime=ajout_pv_id_victime,
                                             id_objet=ajout_pv_id_objet)

        try:
            db.session.add(nouveau_proces_verbal)
            db.session.commit()
            return True, nouveau_proces_verbal

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def modification_proces_verbal(id, update_date, update_id_theatre, update_id_source, update_id_commissaire,
                                   update_id_victime, update_id_objet):
        """
        Fonction pour modifier les informations d'un procès-verbal
        :param id: id du procès-verbal à modifier
        :param update_date: date de rédaction du document
        :param update_id_theatre: id du théâtre où s'est déroulé le vol
        :param update_id_source: id de la cote du document
        :param update_id_commissaire: id du commissaire ayant traité l'affaire
        :param update_id_victime: id de la victime du vol
        :param update_id_objet: id de l'objet convoité
        """
        update_proces_verbal = ProcesVerbal.query.get_or_404(id)
        erreurs = []

        if not update_date:
            erreurs.append(
                "Veuillez renseigner la date du procès-verbal à enregistrer.")
        if not len(update_date) == 10:
            erreurs.append("La cote doit prendre la forme suivante : AAAA-MM-JJ, ex :\"1784-04-06\" (10 caractères).")
        if not (update_date.startswith('177') or update_date.startswith('178')):
            erreurs.append(
                "Veuillez renseigner une date valide (entre 1770 et 1789).")

        if update_proces_verbal.date_pv == update_date and update_proces_verbal.id_theatre == update_id_theatre \
                and update_proces_verbal.id_source == update_id_source \
                and update_proces_verbal.id_commissaire == update_id_commissaire \
                and update_proces_verbal.id_victime == update_id_victime \
                and update_proces_verbal.id_objet == update_id_objet:
            erreurs.append("Aucun changement n'a été effectué.")

        if len(erreurs) > 0:
            return False, erreurs

        update_proces_verbal.date_pv = update_date
        update_proces_verbal.id_theatre = update_id_theatre
        update_proces_verbal.id_source = update_id_source
        update_proces_verbal.id_commissaire = update_id_commissaire
        update_proces_verbal.id_victime = update_id_victime
        update_proces_verbal.id_objet = update_id_objet

        try:
            db.session.add(update_proces_verbal)
            db.session.add(Authorship(id_proces_verbal=update_proces_verbal.id, id_user=current_user.id))
            db.session.commit()
            return True, update_proces_verbal

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def suppression_proces_verbal(id):
        """
        Fonction pour supprimer un procès-verbal
        :param id: id du procès-verbal à supprimer
        """
        delete_proces_verbal = ProcesVerbal.query.get_or_404(id)

        try:
            db.session.delete(delete_proces_verbal)
            db.session.commit()
            return True

        except Exception as erreur:
            return False, [str(erreur)]


class Source(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    cote = db.Column(db.Text, nullable=False)
    proces_verbaux_sources = db.relationship("ProcesVerbal", back_populates="sources")
    authorships = db.relationship("Authorship", back_populates="source")

    @staticmethod
    def ajout_source(ajout_source_cote):
        """
        Fonction pour ajouter une nouvelle source
        :param ajout_source_cote: cote archivistique à ajouter
        """
        erreurs = []
        if not ajout_source_cote:
            erreurs.append(
                "Veuillez renseigner la cote de cette source.")
        if not (len(ajout_source_cote) == 8 or len(ajout_source_cote) == 7 and ajout_source_cote.startswith('Y ')):
            erreurs.append("La cote doit prendre la forme suivante : \"Y 11601A\" ou \"Y 15665\" (7 ou 8 caractères).")

        nouvelle_source = Source.query.filter(
            Source.cote == ajout_source_cote).count()

        if nouvelle_source > 0:
            erreurs.append("Cette cote existe déjà dans la base de données")

        if len(erreurs) > 0:
            return False, erreurs

        nouvelle_source = Source(cote=ajout_source_cote)

        try:
            db.session.add(nouvelle_source)
            db.session.commit()
            return True, nouvelle_source

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def suppression_source(id):
        """
        Fonction pour supprimer une source
        :param id: id de la source à supprimer
        """
        delete_source = Source.query.get_or_404(id)

        try:
            db.session.delete(delete_source)
            db.session.commit()
            return True

        except Exception as erreur:
            return False, [str(erreur)]


class Objet(db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    proces_verbaux_objets = db.relationship("ProcesVerbal", back_populates="objets")
    authorships = db.relationship("Authorship", back_populates="objet")

    @staticmethod
    def ajout_objet(ajout_objet_type):
        """
        Fonctionpour ajouter un objet à la base de données
        :param ajout_objet_type: type de l'objet à ajouter
        """
        erreurs = []
        if not ajout_objet_type:
            erreurs.append(
                "Veuillez renseigner le type de l'objet.")
        if ajout_objet_type and not ajout_objet_type[0].isupper():
            erreurs.append(
                "Veuillez renseigner le type de l'objet avec une majuscule (ex : Montre).")

        nouvel_objet = Objet.query.filter(
            Objet.type == ajout_objet_type).count()
        if nouvel_objet > 0:
            erreurs.append("Cet objet existe déjà dans la base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        nouvel_objet = Objet(type=ajout_objet_type)

        try:
            db.session.add(nouvel_objet)
            db.session.commit()
            return True, nouvel_objet

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def modification_objet(id, objet_type):
        """
        Fonction pour modifier un objet
        :param id: id de l'objet à modifier
        :param objet_type: type de l'objet
        """
        update_objet = Objet.query.get_or_404(id)
        erreurs = []
        if not objet_type:
            erreurs.append(
                "Veuillez renseigner le type de l'objet.")
        if objet_type and not objet_type[0].isupper():
            erreurs.append(
                "Veuillez renseigner le type de l'objet avec une majuscule (ex : Montre).")

        if update_objet.type == objet_type:
            erreurs.append("Aucun changement n'a été effectué.")

        if len(erreurs) > 0:
            return False, erreurs

        update_objet.type = objet_type

        try:
            db.session.add(update_objet)
            db.session.add(Authorship(id_objet=update_objet.id, id_user=current_user.id))
            db.session.commit()
            return True, update_objet

        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def suppression_objet(id):
        """
        Fonction pour supprimer un objet de la base de données
        :param id: id de l'objet à supprimer
        """
        delete_objet = Objet.query.get(id)

        try:
            db.session.delete(delete_objet)
            db.session.commit()
            return True

        except Exception as erreur:
            return False, [str(erreur)]


# on crée une classe pour référencer la création/modification de données à son auteur
class Authorship(db.Model):
    __tablename__ = "authorship"
    id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    id_proces_verbal = db.Column(db.Integer, db.ForeignKey('proces_verbal.id'))
    id_personne = db.Column(db.Integer, db.ForeignKey('personne.id'))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_salle_theatre = db.Column(db.Integer, db.ForeignKey('salle_theatre.id'))
    id_adresse = db.Column(db.Integer, db.ForeignKey('adresse.id'))
    id_source = db.Column(db.Integer, db.ForeignKey('source.id'))
    id_objet = db.Column(db.Integer, db.ForeignKey('objet.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User", back_populates="authorships")
    personne = db.relationship("Personne", back_populates="authorships")
    adresse = db.relationship("Adresse", back_populates="authorships")
    proces_verbal = db.relationship("ProcesVerbal", back_populates="authorships")
    salle_theatre = db.relationship("SalleTheatre", back_populates="authorships")
    source = db.relationship("Source", back_populates="authorships")
    objet = db.relationship("Objet", back_populates="authorships")
