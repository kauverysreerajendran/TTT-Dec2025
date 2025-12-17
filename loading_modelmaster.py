# load_plating_colors.py
# Place this in: your_app/management/commands/load_plating_colors.py

from django.core.management.base import BaseCommand
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Load plating colors and rejection reasons data into multiple tables across different apps'

    def handle(self, *args, **options):
        # Dictionary to store imported models
        models_to_import = {
            'Plating_Color': None,
            'IP_Rejection_Table': None,
            'Brass_QC_Rejection_Table': None,
            'Brass_Audit_Rejection_Table': None,
            'IQF_Rejection_Table': None,
            'Nickel_QC_Rejection_Table': None,
            'Nickel_Audit_Rejection_Table': None,
            'RecoveryIP_Rejection_Table': None,
            'RecoveryBrass_QC_Rejection_Table': None,
            'RecoveryBrass_Audit_Rejection_Table': None,
            'RecoveryIQF_Rejection_Table': None,
        }
        
        # Try to import each model from its respective app
        model_app_mapping = [
            ('Plating_Color', 'modelmasterapp'),
            ('IP_Rejection_Table', 'InputScreening'),
            ('Brass_QC_Rejection_Table', 'Brass_QC'),
            ('Brass_Audit_Rejection_Table', 'BrassAudit'),
            ('IQF_Rejection_Table', 'IQF'),
            ('Nickel_QC_Rejection_Table', 'Nickel_Inspection'),
            ('Nickel_Audit_Rejection_Table', 'Nickel_Audit'),
            ('RecoveryIP_Rejection_Table', 'Recovery_IS'),
            ('RecoveryBrass_QC_Rejection_Table', 'Recovery_Brass_QC'),
            ('RecoveryBrass_Audit_Rejection_Table', 'Recovery_BrassAudit'),
            ('RecoveryIQF_Rejection_Table', 'Recovery_IQF'),
        ]

        # Import models with individual error handling
        for model_name, app_name in model_app_mapping:
            try:
                module = __import__(f'{app_name}.models', fromlist=[model_name])
                model_class = getattr(module, model_name)
                models_to_import[model_name] = model_class
                self.stdout.write(f"✅ Imported {model_name} from {app_name}")
            except ImportError:
                self.stdout.write(f"⚠️  {model_name} not found in {app_name}")
            except AttributeError:
                self.stdout.write(f"⚠️  {model_name} model not found in {app_name}.models")
            except Exception as e:
                self.stdout.write(f"❌ Error importing {model_name} from {app_name}: {str(e)}")

        # Show which models are not available
        missing_models = [name for name, model in models_to_import.items() if model is None]
        available_models = [name for name, model in models_to_import.items() if model is not None]
        
        if missing_models:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  These tables are not available in DB: {', '.join(missing_models)}"
                )
            )
            
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Available tables: {', '.join(available_models)}"
            )
        )

        # Data definitions
        plating_colors_data = [
            ("BLACK", "N"),
            ("IPS", "S"),
            ("IPG", "Y"),
            ("IP-GUN", "GUN"),
            ("IP-BROWN", "BRN"),
            ("RG", "W"),
            ("IPSIPG", "B"),
            ("IP-BLUE M", "BLU"),
            ("RG-BI", "RGSS"),
            ("IPG-2N", "2N"),
            ("IPSIPG-HN", "HN"),
            ("IP-CORN.GOLD", "CN"),
            ("IP-TITANIUM", "T"),
            ("IPG-HALF.N", "HN"),
            ("ANODISING", "A"),
            ("IP-BLUE INH", "BL01"),
            ("IP-BLUE", "BLU"),
            ("IP-BR ANTI", "BA"),
            ("IP-BRONZE", "BRZ"),
            ("IP-CH.GOLD", "CHG"),
            ("IP-SIL ANTI", "SA"),
            ("IP-LCR", "LCR"),
            ("IP-OGR", "OGR"),
            ("IP-ICE BLUE", "IBL"),
            ("IP-PLUM", "PM01"),
            ("IP-TITANIUM BLUE", "TIN"),
        ]

        ip_rejection_reasons = [
            "VERSION MIXUP",
            "MODEL MIXUP", 
            "NO VERSION",
            "SHORTAGE"
        ]

        brass_rejection_reasons = [
            "DENT",
            "SCRATCH",
            "ETCHING STAINS / FINGER STAINS",
            "BUFFING COMPOUND",
            "BACK SIDE DENT",
            "MATERIAL DEFECT/ OD",
            "WAVINESS",
            "STEP DENT",
            "MGS / DO DENT",
            "RING STAINS",
            "OD (HOOK MILL, SBH MISS)",
            "BURR",
            "OTHERS"
        ]

        nickel_rejection_reasons = [
            "WATER STAINS",
            "WIPING STAINS",
            "PLATING STAINS",
            "SANDBLAST STAIN",
            "DENT",
            "SCR",
            "PLATING ROUGHNESS",
            "PITTING",
            "LEVELLING",
            "FINISH ISSUE",
            "DOSCR/STAINS",
            "OD REJECTION",
            "BUFF COMPOUND",
            "MGS/DO DENT",
            "DAMAGE",
            "D.O. BURR",
            "CRACK",
            "ROUND OFF",
            "STEP ROUGHNESS",
            "OTHERS"
        ]

        # Load data for each available table
        total_created = 0

        # 1. Load Plating Colors
        if models_to_import['Plating_Color']:
            total_created += self.load_plating_colors(models_to_import['Plating_Color'], plating_colors_data)

        # 2. Load IP Rejection Reasons (Main and Recovery)
        ip_tables = [
            ('IP_Rejection_Table', 'IP Rejection'),
            ('RecoveryIP_Rejection_Table', 'Recovery IP Rejection')
        ]
        
        for table_name, display_name in ip_tables:
            if models_to_import[table_name]:
                total_created += self.load_rejection_reasons(
                    models_to_import[table_name], 
                    ip_rejection_reasons, 
                    display_name
                )

        # 3. Load Brass QC/Audit/IQF Rejection Reasons (Main and Recovery)
        brass_tables = [
            ('Brass_QC_Rejection_Table', 'Brass QC'),
            ('Brass_Audit_Rejection_Table', 'Brass Audit'),
            ('IQF_Rejection_Table', 'IQF'),
            ('RecoveryBrass_QC_Rejection_Table', 'Recovery Brass QC'),
            ('RecoveryBrass_Audit_Rejection_Table', 'Recovery Brass Audit'),
            ('RecoveryIQF_Rejection_Table', 'Recovery IQF')
        ]
        
        for table_name, display_name in brass_tables:
            if models_to_import[table_name]:
                total_created += self.load_rejection_reasons(
                    models_to_import[table_name], 
                    brass_rejection_reasons, 
                    display_name
                )

        # 4. Load Nickel QC/Audit Rejection Reasons
        nickel_tables = [
            ('Nickel_QC_Rejection_Table', 'Nickel QC'),
            ('Nickel_Audit_Rejection_Table', 'Nickel Audit')
        ]
        
        for table_name, display_name in nickel_tables:
            if models_to_import[table_name]:
                total_created += self.load_rejection_reasons(
                    models_to_import[table_name], 
                    nickel_rejection_reasons, 
                    display_name
                )

        # Final summary
        loaded_tables = [name for name, model in models_to_import.items() if model is not None]
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 DATA LOADING COMPLETED!'
                f'\n📊 Total records created: {total_created}'
                f'\n✅ Successfully loaded {len(loaded_tables)} tables:'
            )
        )
        
        # Group tables by category for better display
        table_categories = {
            'Master Data': ['Plating_Color'],
            'IP Rejection': ['IP_Rejection_Table', 'RecoveryIP_Rejection_Table'],
            'Brass Rejection': ['Brass_QC_Rejection_Table', 'Brass_Audit_Rejection_Table', 'IQF_Rejection_Table',
                               'RecoveryBrass_QC_Rejection_Table', 'RecoveryBrass_Audit_Rejection_Table', 'RecoveryIQF_Rejection_Table'],
            'Nickel Rejection': ['Nickel_QC_Rejection_Table', 'Nickel_Audit_Rejection_Table']
        }
        
        for category, table_list in table_categories.items():
            loaded_in_category = [table for table in table_list if table in loaded_tables]
            if loaded_in_category:
                self.stdout.write(f"   📂 {category}: {', '.join(loaded_in_category)}")

    def load_plating_colors(self, Plating_Color, plating_colors_data):
        """Load plating colors data"""
        try:
            with transaction.atomic():
                # Clear existing data
                Plating_Color.objects.all().delete()
                self.stdout.write("🗑️  Cleared existing Plating_Color data.")

                created_count = 0
                
                for plating_color, plating_color_internal in plating_colors_data:
                    # Random zone assignment
                    zone_1 = random.choice([True, False])
                    zone_2 = random.choice([True, False])
                    
                    plating_color_obj, created = Plating_Color.objects.get_or_create(
                        plating_color=plating_color,
                        defaults={
                            'plating_color_internal': plating_color_internal,
                            'jig_unload_zone_1': zone_1,
                            'jig_unload_zone_2': zone_2,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            f"   ✅ {plating_color} ({plating_color_internal}) - Zone1: {zone_1}, Zone2: {zone_2}"
                        )

                self.stdout.write(f"🎨 Plating Colors: {created_count} records created\n")
                return created_count
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error loading Plating_Color: {str(e)}')
            )
            return 0

    def load_rejection_reasons(self, Model, rejection_reasons, table_display_name):
        """Load rejection reasons for any rejection table"""
        try:
            with transaction.atomic():
                # Clear existing data
                Model.objects.all().delete()
                self.stdout.write(f"🗑️  Cleared existing {table_display_name} data.")

                created_count = 0
                
                for reason in rejection_reasons:
                    rejection_obj, created = Model.objects.get_or_create(
                        rejection_reason=reason
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"   ✅ {reason}")

                self.stdout.write(f"🚫 {table_display_name}: {created_count} records created\n")
                return created_count
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error loading {table_display_name}: {str(e)}')
            )
            return 0

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload even if data exists',
        )
        parser.add_argument(
            '--tables',
            nargs='+',
            help='Load specific tables only (e.g., --tables Plating_Color IP_Rejection_Table)',
        )