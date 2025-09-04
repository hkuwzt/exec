# Azure Deployment Guide

## Prerequisites

1. Azure account with active subscription
2. Azure CLI installed on your local machine
3. Git repository with your code

## Method 1: Deploy via Azure Portal

### Step 1: Create App Service
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Web App" and select it
4. Fill in the details:
   - **Resource Group**: Create new or use existing
   - **Name**: Choose a unique name (e.g., `course-schedule-manager-yourname`)
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose your preferred region
   - **Pricing Plan**: Free F1 (for testing) or Basic B1 (for production)

### Step 2: Configure Deployment
1. In your App Service, go to "Deployment Center"
2. Choose "GitHub" as source
3. Authorize and select your repository
4. Azure will automatically detect it's a Python app
5. Click "Save" to start deployment

### Step 3: Configure Startup Command
1. Go to "Configuration" > "General settings"
2. Set **Startup Command** to: `gunicorn app:app`
3. Click "Save"

## Method 2: Deploy via Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name course-schedule-rg --location "East US"

# Create App Service plan
az appservice plan create --name course-schedule-plan --resource-group course-schedule-rg --sku F1 --is-linux

# Create web app
az webapp create --resource-group course-schedule-rg --plan course-schedule-plan --name course-schedule-manager-yourname --runtime "PYTHON|3.11"

# Configure deployment from GitHub
az webapp deployment source config --name course-schedule-manager-yourname --resource-group course-schedule-rg --repo-url https://github.com/yourusername/workshop --branch main --manual-integration

# Set startup command
az webapp config set --name course-schedule-manager-yourname --resource-group course-schedule-rg --startup-file "gunicorn app:app"
```

## Method 3: Deploy via VS Code

1. Install "Azure App Service" extension in VS Code
2. Open your project folder
3. Press `Ctrl+Shift+P` and run "Azure App Service: Deploy to Web App"
4. Follow the prompts to create/select App Service
5. VS Code will handle the deployment automatically

## Environment Variables (Optional)

If you need to set environment variables:

1. Go to your App Service in Azure Portal
2. Navigate to "Configuration" > "Application settings"
3. Add any required environment variables
4. Click "Save"

## Custom Domain (Optional)

1. Go to "Custom domains" in your App Service
2. Click "Add custom domain"
3. Follow the instructions to verify domain ownership
4. Configure DNS settings as instructed

## Monitoring and Logs

1. **Application Insights**: Enable for monitoring and analytics
2. **Log Stream**: View real-time logs in Azure Portal
3. **Metrics**: Monitor performance and usage

## Troubleshooting

### Common Issues:

1. **Deployment fails**: Check that `requirements.txt` is present and correct
2. **App won't start**: Verify startup command is set to `gunicorn app:app`
3. **Module not found**: Ensure all dependencies are in `requirements.txt`
4. **Static files not loading**: Check that static file paths are correct
5. **NumPy/Pandas compatibility error**: This is fixed with the specific versions in `requirements.txt`

### NumPy/Pandas Compatibility Fix:
If you encounter the error: `ValueError: numpy.dtype size changed, may indicate binary incompatibility`, this has been resolved by:
- Using numpy==1.24.4 and pandas==1.5.3 (compatible versions)
- Installing numpy first in the startup script
- Using Python 3.11.5 runtime

### View Logs:
```bash
az webapp log tail --name course-schedule-manager-yourname --resource-group course-schedule-rg
```

## Security Considerations

1. **HTTPS**: Azure automatically provides HTTPS
2. **Authentication**: Consider adding Azure AD authentication for production
3. **CORS**: Configure if needed for API access from other domains
4. **Environment Variables**: Store sensitive data as app settings, not in code

## Scaling

1. **Scale Up**: Increase CPU/memory by changing App Service plan
2. **Scale Out**: Add multiple instances for high availability
3. **Auto-scaling**: Configure based on CPU usage or schedule

## Cost Optimization

1. **Free Tier**: Good for development/testing (sleeps after 20 minutes of inactivity)
2. **Basic Tier**: Always-on feature for production
3. **Monitor costs**: Set up billing alerts in Azure Portal

Your application will be available at: `https://your-app-name.azurewebsites.net`
