# Nzila Export Hub - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

### 5. Access the Platform
- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

## 📋 User Roles Overview

### 👤 Admin
- Full system access
- Verify documents
- Manage all users and data
- View all deals and commissions

### 🏢 Dealer
- Add and manage vehicles
- View their own deals
- Track commissions earned
- Update deal status

### 🤝 Broker
- Facilitate deals between dealers and buyers
- Create leads
- Track brokered deals
- View commission earnings

### 🛒 Buyer
- Browse available vehicles
- Create leads for vehicles
- Track their orders
- Monitor shipment status in real-time

## 🔄 Complete Workflow Example

### From Lead to Delivered Vehicle

1. **Buyer browses vehicles**
   - GET /api/vehicles/vehicles/
   - Only sees available vehicles

2. **Buyer creates lead**
   - POST /api/deals/leads/
   ```json
   {
     "vehicle_id": 1,
     "source": "website",
     "notes": "Interested in this car"
   }
   ```

3. **Dealer/Broker contacts buyer**
   - Updates lead status to "contacted"
   - PUT /api/deals/leads/{id}/

4. **Lead converts to deal**
   - POST /api/deals/deals/
   ```json
   {
     "vehicle_id": 1,
     "agreed_price_cad": "24000.00",
     "status": "pending_docs"
   }
   ```

5. **Documents uploaded**
   - POST /api/deals/documents/
   - Required: ID, payment proof, vehicle title

6. **Admin verifies documents**
   - PUT /api/deals/documents/{id}/
   ```json
   {
     "status": "verified"
   }
   ```
   - ✨ **Automated**: Deal status advances automatically

7. **Deal completed**
   - PUT /api/deals/deals/{id}/
   ```json
   {
     "status": "completed"
   }
   ```
   - ✨ **Automated**: Commissions created automatically

8. **Shipment created**
   - POST /api/shipments/shipments/
   ```json
   {
     "deal": 1,
     "tracking_number": "SHIP123456",
     "shipping_company": "Ocean Freight Inc",
     "origin_port": "Port of Montreal",
     "destination_port": "Port of Dakar",
     "destination_country": "Senegal"
   }
   ```

9. **Buyer tracks shipment**
   - GET /api/shipments/shipments/{id}/track/
   - Real-time updates visible

## 🔧 Management Commands

### Check for Stalled Deals
```bash
python manage.py check_stalled
```
Run this daily via cron:
```cron
0 9 * * * cd /path/to/project && python manage.py check_stalled
```

## 🌍 Language Switching

### API Header
```
Accept-Language: fr
```

### Web Interface
Use the language selector in the top-right corner

## 📊 Key Features

### Automated Workflows

#### Document Verification → Deal Advancement
When all required documents are verified:
- Deal automatically advances from `pending_docs` to `docs_verified`
- Notifications sent (if configured)

#### Deal Completion → Commission Creation
When deal status changes to `completed`:
- Dealer commission: 5% of agreed price
- Broker commission: 3% of agreed price (if broker involved)
- Both commissions created automatically with status `pending`

#### Stalled Deal Detection
- **Leads**: Flagged if no update in 7+ days
- **Deals**: Flagged if no update in 14+ days
- Run `check_stalled` command to send follow-up notifications

## 🔐 Security Notes

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS
- [ ] Setup PostgreSQL database
- [ ] Configure file storage (S3 recommended)
- [ ] Setup email backend for notifications
- [ ] Enable CSRF protection
- [ ] Configure CORS properly

## 📱 API Authentication

### Session Authentication (Default)
1. Login via /api-auth/login/
2. Session cookie maintained
3. Include CSRF token in POST/PUT/DELETE requests

### Token Authentication (Optional)
Can be added by installing `djangorestframework-simplejwt`

## 🎨 Customization

### Commission Percentages
Edit `commissions/models.py`:
```python
percentage=Decimal('5.00'),  # Change dealer commission
percentage=Decimal('3.00'),  # Change broker commission
```

### Stalled Thresholds
Edit `deals/models.py`:
```python
threshold = timezone.now() - timedelta(days=7)   # Lead threshold
threshold = timezone.now() - timedelta(days=14)  # Deal threshold
```

## 📈 Monitoring & Analytics

### View Statistics in Admin
- Total vehicles by status
- Active deals by stage
- Commission totals
- Shipment tracking

### API Endpoints for Dashboards
- `/api/vehicles/vehicles/?status=available` - Available inventory
- `/api/deals/deals/?status=pending_docs` - Pending deals
- `/api/commissions/commissions/?status=pending` - Pending commissions

## 🆘 Troubleshooting

### Issue: Tests failing
**Solution**: Make sure all dependencies are installed
```bash
pip install -r requirements.txt
python manage.py test
```

### Issue: Images not uploading
**Solution**: Check MEDIA_ROOT permissions
```bash
mkdir -p media
chmod 755 media
```

### Issue: Translations not working
**Solution**: Compile messages
```bash
python manage.py compilemessages
```

## 📚 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django i18n: https://docs.djangoproject.com/en/4.2/topics/i18n/

## 💡 Tips

1. Use the helper script for common tasks:
   ```bash
   ./manage.sh
   ```

2. Enable Django debug toolbar in development:
   ```bash
   pip install django-debug-toolbar
   ```

3. Use Django shell for testing queries:
   ```bash
   python manage.py shell
   ```

4. Create database backups regularly:
   ```bash
   python manage.py dumpdata > backup.json
   ```

## 🤝 Contributing

When adding new features:
1. Follow the existing app structure
2. Add tests for new functionality
3. Use Django signals for automation
4. Mark strings with gettext_lazy for translation
5. Use Decimal for monetary values
6. Update API documentation

## 📞 Support

For technical support, contact the development team or create an issue in the repository.
