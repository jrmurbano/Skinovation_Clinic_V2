from django.core.management.base import BaseCommand
from packages.models import Package

class Command(BaseCommand):
    help = 'Import packages from original data'

    def handle(self, *args, **options):
        # Sample packages data matching the original
        packages_data = [
            {
                'package_name': '3 + 1 Underarm Whitening',
                'description': 'N/A',
                'price': 1847.00,
                'sessions': 4,
                'duration_days': 0,
                'grace_period_days': 0,
            },
            {
                'package_name': '3 + 1 Back Whitening',
                'description': 'N/A',
                'price': 1847.00,
                'sessions': 4,
                'duration_days': 0,
                'grace_period_days': 0,
            },
            {
                'package_name': '3 + 1 Bikini Whitening',
                'description': 'N/A',
                'price': 1847.00,
                'sessions': 4,
                'duration_days': 0,
                'grace_period_days': 0,
            },
        ]

        for package_data in packages_data:
            # Check if package already exists
            existing_packages = Package.objects.filter(package_name=package_data['package_name'])
            if existing_packages.exists():
                # Update the first one if it exists
                package = existing_packages.first()
                package.description = package_data['description']
                package.price = package_data['price']
                package.sessions = package_data['sessions']
                package.duration_days = package_data['duration_days']
                package.grace_period_days = package_data['grace_period_days']
                package.save()
                self.stdout.write(f'Updated package: {package.package_name}')
            else:
                # Create new package
                package = Package.objects.create(
                    package_name=package_data['package_name'],
                    description=package_data['description'],
                    price=package_data['price'],
                    sessions=package_data['sessions'],
                    duration_days=package_data['duration_days'],
                    grace_period_days=package_data['grace_period_days'],
                )
                self.stdout.write(f'Created package: {package.package_name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully imported packages')
        )
