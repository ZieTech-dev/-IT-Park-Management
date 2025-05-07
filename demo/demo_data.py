# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_date(days=0, months=0):
    """Fonction utilitaire pour générer des dates relatives à aujourd'hui"""
    return (datetime.now() + timedelta(days=days) + relativedelta(months=months)).strftime('%Y-%m-%d')

def load_demo_data(cr, registry):
    """Fonction pour charger les données de démonstration"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Création des types d'équipements
        equipment_types = [
            env['it.equipment.type'].create({
                'name': 'Ordinateur portable',
                'code': 'LAPTOP',
                'description': 'Ordinateurs portables professionnels',
            }),
            env['it.equipment.type'].create({
                'name': 'Poste fixe',
                'code': 'DESKTOP',
                'description': 'Ordinateurs de bureau professionnels',
            }),
            env['it.equipment.type'].create({
                'name': 'Serveur',
                'code': 'SERVER',
                'description': 'Serveurs physiques',
            }),
            env['it.equipment.type'].create({
                'name': 'Imprimante',
                'code': 'PRINTER',
                'description': 'Imprimantes et multifonctions',
            }),
            env['it.equipment.type'].create({
                'name': 'Téléphone',
                'code': 'PHONE',
                'description': 'Téléphones mobiles professionnels',
            }),
        ]
        
        # Création des marques d'équipements
        equipment_brands = [
            env['it.equipment.brand'].create({
                'name': 'Dell',
                'website': 'https://www.dell.com',
            }),
            env['it.equipment.brand'].create({
                'name': 'HP',
                'website': 'https://www.hp.com',
            }),
            env['it.equipment.brand'].create({
                'name': 'Lenovo',
                'website': 'https://www.lenovo.com',
            }),
            env['it.equipment.brand'].create({
                'name': 'Apple',
                'website': 'https://www.apple.com',
            }),
            env['it.equipment.brand'].create({
                'name': 'Brother',
                'website': 'https://www.brother.com',
            }),
            env['it.equipment.brand'].create({
                'name': 'Samsung',
                'website': 'https://www.samsung.com',
            }),
        ]
        
        # Création des catégories de logiciels
        software_categories = [
            env['it.software.category'].create({
                'name': 'Système d\'exploitation',
                'description': 'OS pour postes de travail et serveurs',
            }),
            env['it.software.category'].create({
                'name': 'Suite bureautique',
                'description': 'Applications de traitement de texte, tableur, etc.',
            }),
            env['it.software.category'].create({
                'name': 'Sécurité',
                'description': 'Antivirus, firewall, etc.',
            }),
            env['it.software.category'].create({
                'name': 'Développement',
                'description': 'IDE, compilateurs, etc.',
            }),
            env['it.software.category'].create({
                'name': 'Utilitaires',
                'description': 'Outils variés pour la productivité',
            }),
        ]
        
        # Création des éditeurs de logiciels
        software_editors = [
            env['it.software.editor'].create({
                'name': 'Microsoft',
                'website': 'https://www.microsoft.com',
            }),
            env['it.software.editor'].create({
                'name': 'Adobe',
                'website': 'https://www.adobe.com',
            }),
            env['it.software.editor'].create({
                'name': 'Oracle',
                'website': 'https://www.oracle.com',
            }),
            env['it.software.editor'].create({
                'name': 'JetBrains',
                'website': 'https://www.jetbrains.com',
            }),
            env['it.software.editor'].create({
                'name': 'Symantec',
                'website': 'https://www.symantec.com',
            }),
        ]
        
        # Création des types de contrats
        contract_types = [
            env['it.contract.type'].create({
                'name': 'Maintenance',
                'description': 'Contrat de maintenance matérielle',
            }),
            env['it.contract.type'].create({
                'name': 'Support',
                'description': 'Contrat de support technique',
            }),
            env['it.contract.type'].create({
                'name': 'Licence',
                'description': 'Contrat de licence logicielle',
            }),
            env['it.contract.type'].create({
                'name': 'Infogérance',
                'description': 'Contrat d\'infogérance complète',
            }),
            env['it.contract.type'].create({
                'name': 'SLA',
                'description': 'Contrat de niveau de service',
            }),
        ]
        
        # Création des types d'alertes
        alert_types = [
            env['it.alert.type'].create({
                'name': 'Fin de garantie',
                'description': 'Alerte de fin de garantie pour les équipements',
                'model': 'it.equipment',
                'days_before': 30,
                'color': '#FF9F40',
            }),
            env['it.alert.type'].create({
                'name': 'Expiration de licence',
                'description': 'Alerte d\'expiration de licence logicielle',
                'model': 'it.software',
                'days_before': 30,
                'color': '#F06050',
            }),
            env['it.alert.type'].create({
                'name': 'Fin de contrat',
                'description': 'Alerte de fin de contrat',
                'model': 'it.contract',
                'days_before': 60,
                'color': '#875A7B',
            }),
            env['it.alert.type'].create({
                'name': 'Renouvellement',
                'description': 'Alerte de renouvellement',
                'model': 'it.contract',
                'days_before': 90,
                'color': '#3CABDB',
            }),
        ]
        
        # Création des types d'interventions
        intervention_types = [
            env['it.intervention.type'].create({
                'name': 'Installation',
                'description': 'Installation de matériel ou logiciel',
                'color': '#5CB85C',
            }),
            env['it.intervention.type'].create({
                'name': 'Dépannage',
                'description': 'Intervention de dépannage',
                'color': '#D9534F',
            }),
            env['it.intervention.type'].create({
                'name': 'Maintenance',
                'description': 'Maintenance préventive',
                'color': '#5BC0DE',
            }),
            env['it.intervention.type'].create({
                'name': 'Formation',
                'description': 'Formation utilisateur',
                'color': '#F0AD4E',
            }),
            env['it.intervention.type'].create({
                'name': 'Mise à jour',
                'description': 'Mise à jour matérielle ou logicielle',
                'color': '#337AB7',
            }),
        ]
        
        # Création des priorités d'interventions
        intervention_priorities = [
            env['it.intervention.priority'].create({
                'name': 'Critique',
                'sequence': 1,
                'color': '#FF0000',
                'response_time_hours': 1,
                'resolution_time_hours': 4,
            }),
            env['it.intervention.priority'].create({
                'name': 'Haute',
                'sequence': 2,
                'color': '#FFA500',
                'response_time_hours': 4,
                'resolution_time_hours': 8,
            }),
            env['it.intervention.priority'].create({
                'name': 'Moyenne',
                'sequence': 3,
                'color': '#FFFF00',
                'response_time_hours': 8,
                'resolution_time_hours': 24,
            }),
            env['it.intervention.priority'].create({
                'name': 'Basse',
                'sequence': 4,
                'color': '#00FF00',
                'response_time_hours': 24,
                'resolution_time_hours': 72,
            }),
            env['it.intervention.priority'].create({
                'name': 'Planifiée',
                'sequence': 5,
                'color': '#0000FF',
                'response_time_hours': 48,
                'resolution_time_hours': 120,
            }),
        ]
        
        # Création des partenaires (entreprises)
        partners = [
            env['res.partner'].create({
                'name': 'TechSolutions SA',
                'street': '12 rue de l\'Innovation',
                'zip': '75001',
                'city': 'Paris',
                'country_id': env.ref('base.fr').id,
                'email': 'contact@techsolutions.example.com',
                'phone': '+33123456789',
                'is_company': True,
            }),
            env['res.partner'].create({
                'name': 'Industrie & Co',
                'street': '45 avenue de la Productivité',
                'zip': '69002',
                'city': 'Lyon',
                'country_id': env.ref('base.fr').id,
                'email': 'info@industrieco.example.com',
                'phone': '+33234567890',
                'is_company': True,
            }),
            env['res.partner'].create({
                'name': 'Finance Express',
                'street': '78 boulevard des Finances',
                'zip': '44000',
                'city': 'Nantes',
                'country_id': env.ref('base.fr').id,
                'email': 'contact@financeexpress.example.com',
                'phone': '+33345678901',
                'is_company': True,
            }),
        ]
        
        # Création des contacts pour les partenaires
        contacts = []
        
        # Contacts pour TechSolutions SA
        contacts.append(env['res.partner'].create({
            'name': 'Jean Dupont',
            'function': 'Directeur IT',
            'email': 'jean.dupont@techsolutions.example.com',
            'phone': '+33123456701',
            'mobile': '+33611223344',
            'parent_id': partners[0].id,
            'is_company': False,
        }))
        
        contacts.append(env['res.partner'].create({
            'name': 'Marie Martin',
            'function': 'Responsable Infrastructure',
            'email': 'marie.martin@techsolutions.example.com',
            'phone': '+33123456702',
            'mobile': '+33622334455',
            'parent_id': partners[0].id,
            'is_company': False,
        }))
        
        # Contacts pour Industrie & Co
        contacts.append(env['res.partner'].create({
            'name': 'Pierre Dubois',
            'function': 'DSI',
            'email': 'pierre.dubois@industrieco.example.com',
            'phone': '+33234567801',
            'mobile': '+33633445566',
            'parent_id': partners[1].id,
            'is_company': False,
        }))
        
        contacts.append(env['res.partner'].create({
            'name': 'Sophie Leroy',
            'function': 'Administrateur Système',
            'email': 'sophie.leroy@industrieco.example.com',
            'phone': '+33234567802',
            'mobile': '+33644556677',
            'parent_id': partners[1].id,
            'is_company': False,
        }))
        
        # Contacts pour Finance Express
        contacts.append(env['res.partner'].create({
            'name': 'Thomas Moreau',
            'function': 'Responsable IT',
            'email': 'thomas.moreau@financeexpress.example.com',
            'phone': '+33345678902',
            'mobile': '+33655667788',
            'parent_id': partners[2].id,
            'is_company': False,
        }))
        
        contacts.append(env['res.partner'].create({
            'name': 'Julie Petit',
            'function': 'Support Technique',
            'email': 'julie.petit@financeexpress.example.com',
            'phone': '+33345678903',
            'mobile': '+33666778899',
            'parent_id': partners[2].id,
            'is_company': False,
        }))
        
        # Création des clients IT
        clients = [
            env['it.client'].create({
                'name': 'TechSolutions',
                'partner_id': partners[0].id,
            }),
            env['it.client'].create({
                'name': 'Industrie & Co',
                'partner_id': partners[1].id,
            }),
            env['it.client'].create({
                'name': 'Finance Express',
                'partner_id': partners[2].id,
            }),
        ]
        
        # Création des contacts clients
        client_contacts = []
        
        # Contacts pour TechSolutions
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[0].id,
            'partner_id': contacts[0].id,
            'function': 'Directeur IT',
            'is_primary': True,
            'is_technical': True,
        }))
        
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[0].id,
            'partner_id': contacts[1].id,
            'function': 'Responsable Infrastructure',
            'is_technical': True,
        }))
        
        # Contacts pour Industrie & Co
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[1].id,
            'partner_id': contacts[2].id,
            'function': 'DSI',
            'is_primary': True,
            'is_billing': True,
        }))
        
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[1].id,
            'partner_id': contacts[3].id,
            'function': 'Administrateur Système',
            'is_technical': True,
        }))
        
        # Contacts pour Finance Express
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[2].id,
            'partner_id': contacts[4].id,
            'function': 'Responsable IT',
            'is_primary': True,
            'is_technical': True,
            'is_billing': True,
        }))
        
        client_contacts.append(env['it.client.contact'].create({
            'client_id': clients[2].id,
            'partner_id': contacts[5].id,
            'function': 'Support Technique',
            'is_technical': True,
        }))
        
        # Création des sites clients
        sites = []
        
        # Sites pour TechSolutions
        sites.append(env['it.client.site'].create({
            'name': 'Siège Social',
            'client_id': clients[0].id,
            'address': '12 rue de l\'Innovation',
            'zip': '75001',
            'city': 'Paris',
            'country_id': env.ref('base.fr').id,
            'contact_id': client_contacts[0].id,
        }))
        
        sites.append(env['it.client.site'].create({
            'name': 'Data Center',
            'client_id': clients[0].id,
            'address': '5 rue des Serveurs',
            'zip': '92300',
            'city': 'Levallois-Perret',
            'country_id': env.ref('base.fr').id,
            'contact_id': client_contacts[1].id,
        }))
        
        # Sites pour Industrie & Co
        sites.append(env['it.client.site'].create({
            'name': 'Siège Lyon',
            'client_id': clients[1].id,
            'address': '45 avenue de la Productivité',
            'zip': '69002',
            'city': 'Lyon',
            'country_id': env.ref('base.fr').id,
            'contact_id': client_contacts[2].id,
        }))
        
        sites.append(env['it.client.site'].create({
            'name': 'Usine Marseille',
            'client_id': clients[1].id,
            'address': '123 route de la Fabrication',
            'zip': '13016',
            'city': 'Marseille',
            'country_id': env.ref('base.fr').id,
            'contact_id': client_contacts[3].id,
        }))
        
        # Sites pour Finance Express
        sites.append(env['it.client.site'].create({
            'name': 'Siège Nantes',
            'client_id': clients[2].id,
            'address': '78 boulevard des Finances',
            'zip': '44000',
            'city': 'Nantes',
            'country_id': env.ref('base.fr').id,
            'contact_id': client_contacts[4].id,
        }))
        
        # Création des équipements
        equipments = []
        
        # Équipements pour TechSolutions
        # Portables
        for i in range(1, 6):
            equipments.append(env['it.equipment'].create({
                'name': f'Laptop DEV-{i}',
                'client_id': clients[0].id,
                'site_id': sites[0].id,
                'type_id': equipment_types[0].id,  # Ordinateur portable
                'brand_id': equipment_brands[0].id,  # Dell
                'model': 'XPS 15',
                'serial_number': f'DELL-XPS15-{i}',
                'purchase_date': get_date(days=-365),
                'installation_date': get_date(days=-360),
                'warranty_end': get_date(days=365),
                'state': 'in_use',
                'purchase_cost': 1500.0,
                'ip_address': f'192.168.1.{10+i}',
                'technical_specs': 'Intel Core i7, 16GB RAM, 512GB SSD, Windows 11 Pro',
            }))
        
        # Serveurs
        for i in range(1, 4):
            equipments.append(env['it.equipment'].create({
                'name': f'SRV-APP-{i}',
                'client_id': clients[0].id,
                'site_id': sites[1].id,
                'type_id': equipment_types[2].id,  # Serveur
                'brand_id': equipment_brands[1].id,  # HP
                'model': 'ProLiant DL380',
                'serial_number': f'HP-DL380-{i}',
                'purchase_date': get_date(days=-730),
                'installation_date': get_date(days=-720),
                'warranty_end': get_date(days=180),
                'state': 'in_use',
                'purchase_cost': 4500.0,
                'ip_address': f'192.168.10.{i}',
                'technical_specs': 'Intel Xeon Silver, 64GB RAM, 4TB SSD RAID, Windows Server 2022',
            }))
        
        # Équipements pour Industrie & Co
        # Postes fixes
        for i in range(1, 11):
            equipments.append(env['it.equipment'].create({
                'name': f'PC-ADM-{i}',
                'client_id': clients[1].id,
                'site_id': sites[2].id,
                'type_id': equipment_types[1].id,  # Poste fixe
                'brand_id': equipment_brands[2].id,  # Lenovo
                'model': 'ThinkCentre M720',
                'serial_number': f'LEN-M720-{i}',
                'purchase_date': get_date(days=-180),
                'installation_date': get_date(days=-175),
                'warranty_end': get_date(days=550),
                'state': 'in_use',
                'purchase_cost': 850.0,
                'ip_address': f'192.168.20.{i}',
                'technical_specs': 'Intel Core i5, 8GB RAM, 256GB SSD, Windows 10 Pro',
            }))
        
        # Imprimantes
        equipments.append(env['it.equipment'].create({
            'name': 'IMP-ACCUEIL',
            'client_id': clients[1].id,
            'site_id': sites[2].id,
            'type_id': equipment_types[3].id,  # Imprimante
            'brand_id': equipment_brands[4].id,  # Brother
            'model': 'MFC-L8900CDW',
            'serial_number': 'BRO-L8900-001',
            'purchase_date': get_date(days=-90),
            'installation_date': get_date(days=-88),
            'warranty_end': get_date(days=640),
            'state': 'in_use',
            'purchase_cost': 599.0,
            'ip_address': '192.168.20.100',
            'technical_specs': 'Imprimante laser couleur multifonction, recto-verso, réseau, wifi',
        }))
        
        # Équipements pour Finance Express
        # Portables haut de gamme
        for i in range(1, 6):
            equipments.append(env['it.equipment'].create({
                'name': f'MBA-FIN-{i}',
                'client_id': clients[2].id,
                'site_id': sites[4].id,
                'type_id': equipment_types[0].id,  # Ordinateur portable
                'brand_id': equipment_brands[3].id,  # Apple
                'model': 'MacBook Air M2',
                'serial_number': f'APP-MBAM2-{i}',
                'purchase_date': get_date(days=-60),
                'installation_date': get_date(days=-58),
                'warranty_end': get_date(days=670),
                'state': 'in_use',
                'purchase_cost': 1299.0,
                'ip_address': f'192.168.30.{i}',
                'technical_specs': 'Apple M2, 16GB RAM, 512GB SSD, macOS Ventura',
            }))
        
        # Téléphones
        for i in range(1, 4):
            equipments.append(env['it.equipment'].create({
                'name': f'IP{i}',
                'client_id': clients[2].id,
                'site_id': sites[4].id,
                'type_id': equipment_types[4].id,  # Téléphone
                'brand_id': equipment_brands[5].id,  # Samsung
                'model': 'Galaxy S22',
                'serial_number': f'SAM-S22-{i}',
                'purchase_date': get_date(days=-120),
                'installation_date': get_date(days=-118),
                'warranty_end': get_date(days=610),
                'state': 'in_use',
                'purchase_cost': 799.0,
                'technical_specs': '6.1", 8GB RAM, 128GB, Android 12',
            }))
        
        # Création des logiciels
        softwares = []
        
        # Logiciels pour TechSolutions
        softwares.append(env['it.software'].create({
            'name': 'Windows 11 Pro',
            'client_id': clients[0].id,
            'category_id': software_categories[0].id,  # Système d'exploitation
            'editor_id': software_editors[0].id,  # Microsoft
            'version': '22H2',
            'license_type': 'perpetual',
            'purchase_date': get_date(days=-365),
            'purchase_cost': 5000.0,  # License en volume
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[:5]])],  # Associer aux 5 laptops
        }))
        
        softwares.append(env['it.software'].create({
            'name': 'Microsoft 365 Business',
            'client_id': clients[0].id,
            'category_id': software_categories[1].id,  # Suite bureautique
            'editor_id': software_editors[0].id,  # Microsoft
            'version': '2023',
            'license_type': 'subscription',
            'purchase_date': get_date(days=-180),
            'expiration_date': get_date(days=185),
            'purchase_cost': 1500.0,
            'renewal_cost': 1500.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[:5]])],  # Associer aux 5 laptops
        }))
        
        softwares.append(env['it.software'].create({
            'name': 'Windows Server 2022 Datacenter',
            'client_id': clients[0].id,
            'category_id': software_categories[0].id,  # Système d'exploitation
            'editor_id': software_editors[0].id,  # Microsoft
            'version': '21H2',
            'license_type': 'perpetual',
            'purchase_date': get_date(days=-730),
            'purchase_cost': 6000.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[5:8]])],  # Associer aux 3 serveurs
        }))
        
        # Logiciels pour Industrie & Co
        softwares.append(env['it.software'].create({
            'name': 'Windows 10 Pro',
            'client_id': clients[1].id,
            'category_id': software_categories[0].id,  # Système d'exploitation
            'editor_id': software_editors[0].id,  # Microsoft
            'version': '21H2',
            'license_type': 'perpetual',
            'purchase_date': get_date(days=-180),
            'purchase_cost': 3500.0,  # License en volume
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[8:18]])],  # Associer aux 10 postes fixes
        }))
        
        softwares.append(env['it.software'].create({
            'name': 'Adobe Creative Cloud',
            'client_id': clients[1].id,
            'category_id': software_categories[4].id,  # Utilitaires
            'editor_id': software_editors[1].id,  # Adobe
            'version': '2023',
            'license_type': 'subscription',
            'purchase_date': get_date(days=-90),
            'expiration_date': get_date(days=275),
            'purchase_cost': 1200.0,
            'renewal_cost': 1200.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [equipments[8].id, equipments[9].id])],  # Associer à 2 postes fixes
        }))
        
        # Logiciels pour Finance Express
        softwares.append(env['it.software'].create({
            'name': 'macOS Ventura',
            'client_id': clients[2].id,
            'category_id': software_categories[0].id,  # Système d'exploitation
            'editor_id': software_editors[3].id,  # Apple
            'version': '13.0',
            'license_type': 'perpetual',
            'purchase_date': get_date(days=-60),
            'purchase_cost': 0.0,  # Inclus avec le matériel
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[19:24]])],  # Associer aux 5 MacBooks
        }))
        
        softwares.append(env['it.software'].create({
            'name': 'Microsoft 365 Enterprise',
            'client_id': clients[2].id,
            'category_id': software_categories[1].id,  # Suite bureautique
            'editor_id': software_editors[0].id,  # Microsoft
            'version': '2023',
            'license_type': 'subscription',
            'purchase_date': get_date(days=-30),
            'expiration_date': get_date(days=335),
            'purchase_cost': 2500.0,
            'renewal_cost': 2500.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[19:24]])],  # Associer aux 5 MacBooks
        }))
        
        softwares.append(env['it.software'].create({
            'name': 'Symantec Endpoint Protection',
            'client_id': clients[2].id,
            'category_id': software_categories[2].id,  # Sécurité
            'editor_id': software_editors[4].id,  # Symantec
            'version': '15.0',
            'license_type': 'subscription',
            'purchase_date': get_date(days=-30),
            'expiration_date': get_date(days=335),
            'purchase_cost': 1800.0,
            'renewal_cost': 1800.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[19:24]])],  # Associer aux 5 MacBooks
        }))
        
        # Création des contrats
        contracts = []
        
        # Contrats pour TechSolutions
        contracts.append(env['it.contract'].create({
            'name': 'Maintenance Serveurs',
            'client_id': clients[0].id,
            'type_id': contract_types[0].id,  # Maintenance
            'date_start': get_date(days=-365),
            'date_end': get_date(days=365),
            'invoicing_frequency': 'quarterly',
            'price': 4800.0,
            'recurring_amount': 1200.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[5:8]])],  # Serveurs
            'description': 'Contrat de maintenance préventive et curative pour les serveurs du data center',
            'sla_response_time': '4',
            'sla_resolution_time': '24',
        }))
        
        contracts.append(env['it.contract'].create({
            'name': 'Support Technique',
            'client_id': clients[0].id,
            'type_id': contract_types[1].id,  # Support
            'date_start': get_date(days=-180),
            'date_end': get_date(days=185),
            'invoicing_frequency': 'monthly',
            'price': 12000.0,
            'recurring_amount': 1000.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[:5]])],  # Laptops
            'description': 'Contrat de support technique pour les postes de travail des développeurs',
            'sla_response_time': '2',
            'sla_resolution_time': '8',
        }))
        
        # Contrat pour Industrie & Co
        contracts.append(env['it.contract'].create({
            'name': 'Infogérance Complète',
            'client_id': clients[1].id,
            'type_id': contract_types[3].id,  # Infogérance
            'date_start': get_date(days=-90),
            'date_end': get_date(days=640),
            'invoicing_frequency': 'monthly',
            'price': 24000.0,
            'recurring_amount': 2000.0,
            'state': 'active',
            'equipment_ids': [(6, 0, [e.id for e in equipments[8:18]])],  # Postes fixes
            'software_ids': [(6, 0, [softwares[3].id, softwares[4].id])],  # Logiciels Windows + Adobe
            'description': 'Contrat d\'infogérance complète incluant maintenance, support et supervision',
            'sla_response_time': '1',
            'sla_resolution_time': '4',
        }))
        
        # Contrat pour Finance Express
        contracts.append(env['it.contract'].create({
            'name': 'Licence Microsoft 365',
            'client_id': clients[2].id,
            'type_id': contract_types[2].id,  # Licence
            'date_start': get_date(days=-30),
            'date_end': get_date(days=335),
            'invoicing_frequency': 'annual',
            'price': 2500.0,
            'recurring_amount': 2500.0,
            'state': 'active',
            'software_ids': [(6, 0, [softwares[7].id])],  # Microsoft 365
            'description': 'Contrat de licence pour Microsoft 365 Enterprise',
        }))
        
        contracts.append(env['it.contract'].create({
            'name': 'SLA Premium',
            'client_id': clients[2].id,
            'type_id': contract_types[4].id,  # SLA
            'date_start': get_date(days=-60),
            'date_end': get_date(days=-10),
            'invoicing_frequency': 'monthly',
            'price': 15000.0,
            'recurring_amount': 3000.0,
            'state': 'expired',
            'equipment_ids': [(6, 0, [e.id for e in equipments[19:24]])],  # MacBooks
            'description': 'Contrat de niveau de service premium pour les postes de travail de la direction',
            'sla_response_time': '0',  # Immédiat
            'sla_resolution_time': '4',
        }))
        
        # Un contrat qui expire bientôt pour tester les alertes
        contracts.append(env['it.contract'].create({
            'name': 'Support Antivirus',
            'client_id': clients[2].id,
            'type_id': contract_types[1].id,  # Support
            'date_start': get_date(days=-335),
            'date_end': get_date(days=25),
            'invoicing_frequency': 'annual',
            'price': 1800.0,
            'recurring_amount': 1800.0,
            'state': 'to_renew',
            'software_ids': [(6, 0, [softwares[8].id])],  # Symantec
            'description': 'Contrat de support pour la solution antivirus',
        }))
        
        # Création des alertes
        alerts = []
        
        # Alerte fin de garantie
        alerts.append(env['it.alert'].create({
            'name': 'Fin de garantie - SRV-APP-1',
            'type_id': alert_types[0].id,
            'client_id': clients[0].id,
            'res_model': 'it.equipment',
            'res_id': equipments[5].id,
            'equipment_id': equipments[5].id,
            'date': get_date(days=180),
            'state': 'draft',
            'description': f'La garantie du serveur SRV-APP-1 expire le {get_date(days=180)}.',
        }))
        
        # Alerte expiration de licence
        alerts.append(env['it.alert'].create({
            'name': 'Expiration de licence - Microsoft 365 Business',
            'type_id': alert_types[1].id,
            'client_id': clients[0].id,
            'res_model': 'it.software',
            'res_id': softwares[1].id,
            'software_id': softwares[1].id,
            'date': get_date(days=185),
            'state': 'draft',
            'description': f'La licence Microsoft 365 Business expire le {get_date(days=185)}.',
        }))
        
        # Alerte fin de contrat
        alerts.append(env['it.alert'].create({
            'name': 'Fin de contrat - Support Antivirus',
            'type_id': alert_types[2].id,
            'client_id': clients[2].id,
            'res_model': 'it.contract',
            'res_id': contracts[5].id,
            'contract_id': contracts[5].id,
            'date': get_date(days=25),
            'state': 'draft',
            'description': f'Le contrat Support Antivirus expire le {get_date(days=25)}.',
        }))
        
        # Création des interventions
        interventions = []
        
        # Intervention pour TechSolutions
        interventions.append(env['it.intervention'].create({
            'name': 'Installation nouvelle version Windows Server',
            'client_id': clients[0].id,
            'equipment_id': equipments[6].id,
            'type_id': intervention_types[4].id,  # Mise à jour
            'priority_id': intervention_priorities[2].id,  # Moyenne
            'user_id': env.user.id,
            'date_start': get_date(days=-45),
            'date_end': get_date(days=-45, months=0) + ' 04:30:00',
            'planned_duration': 4.0,
            'state': 'closed',
            'description': '<p>Installation de la mise à jour Windows Server 2022 avec derniers correctifs</p>',
            'solution': '<p>Mise à jour effectuée avec succès. Redémarrage du serveur effectué et tous les services vérifiés.</p>',
        }))
        
        # Intervention pour Industrie & Co
        interventions.append(env['it.intervention'].create({
            'name': 'Dépannage imprimante',
            'client_id': clients[1].id,
            'equipment_id': equipments[18].id,
            'type_id': intervention_types[1].id,  # Dépannage
            'priority_id': intervention_priorities[1].id,  # Haute
            'user_id': env.user.id,
            'date_start': get_date(days=-10),
            'date_end': get_date(days=-10, months=0) + ' 02:15:00',
            'planned_duration': 2.0,
            'state': 'closed',
            'description': '<p>L\'imprimante affiche une erreur de bourrage papier mais aucun papier n\'est visible</p>',
            'cause': 'Capteur de papier défectueux',
            'solution': '<p>Remplacement du capteur de papier et recalibration complète de l\'imprimante. Tests effectués avec succès.</p>',
        }))
        
        # Intervention en cours pour Finance Express
        interventions.append(env['it.intervention'].create({
            'name': 'Formation Microsoft 365',
            'client_id': clients[2].id,
            'software_id': softwares[7].id,
            'type_id': intervention_types[3].id,  # Formation
            'priority_id': intervention_priorities[4].id,  # Planifiée
            'user_id': env.user.id,
            'date_start': get_date(days=-2),
            'planned_duration': 7.0,
            'state': 'in_progress',
            'description': '<p>Formation des utilisateurs sur les nouvelles fonctionnalités de Microsoft 365</p>',
        }))
        
        # Intervention planifiée pour Finance Express
        interventions.append(env['it.intervention'].create({
            'name': 'Mise à jour antivirus',
            'client_id': clients[2].id,
            'software_id': softwares[8].id,
            'type_id': intervention_types[4].id,  # Mise à jour
            'priority_id': intervention_priorities[3].id,  # Basse
            'user_id': env.user.id,
            'date_start': get_date(days=5),
            'planned_duration': 2.0,
            'state': 'assigned',
            'description': '<p>Mise à jour de la solution antivirus vers la dernière version</p>',
        }))
        
        # Intervention urgente pour TechSolutions
        interventions.append(env['it.intervention'].create({
            'name': 'Panne serveur de production',
            'client_id': clients[0].id,
            'equipment_id': equipments[5].id,
            'type_id': intervention_types[1].id,  # Dépannage
            'priority_id': intervention_priorities[0].id,  # Critique
            'user_id': env.user.id,
            'date_start': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'planned_duration': 3.0,
            'state': 'assigned',
            'description': '<p>Le serveur ne répond plus suite à une coupure de courant</p>',
        }))
        
        # Logs de l'installation des données
        print('✅ Données de démonstration du module de gestion de parc IT chargées avec succès')
        print(f'   - {len(clients)} clients créés')
        print(f'   - {len(sites)} sites créés')
        print(f'   - {len(equipments)} équipements créés')
        print(f'   - {len(softwares)} logiciels créés')
        print(f'   - {len(contracts)} contrats créés')
        print(f'   - {len(alerts)} alertes créées')
        print(f'   - {len(interventions)} interventions créées')

            