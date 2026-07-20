pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        EB_APP_NAME        = 'app2'
        EB_ENV_NAME        = 'App2-env'
        S3_BUCKET          = 'elasticbeanstalk-us-east-1-139822120014'
        ZIP_NAME           = "beanstalk-deploy-${BUILD_NUMBER}.zip"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code checked out from main branch"
            }
        }

        stage('Package') {
            steps {
                echo "📦 Creating deployment ZIP..."

                bat """
                if exist %ZIP_NAME% del /f /q %ZIP_NAME%

                powershell -Command ^
                "Compress-Archive -Path * -DestinationPath '%ZIP_NAME%' -Force"
                """

                echo "✅ ZIP created: ${ZIP_NAME}"
            }
        }

        stage('Upload to S3') {
            steps {
                echo "☁️ Uploading ZIP to S3..."

                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {

                    bat """
                    aws s3 cp %ZIP_NAME% s3://%S3_BUCKET%/deployments/%ZIP_NAME% --region %AWS_DEFAULT_REGION%
                    """
                }

                echo "✅ Upload complete"
            }
        }

        stage('Deploy to Elastic Beanstalk') {
            steps {
                echo "🚀 Deploying to Elastic Beanstalk..."

                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {

                    bat """
                    aws elasticbeanstalk create-application-version ^
                      --application-name "%EB_APP_NAME%" ^
                      --version-label "v-build-%BUILD_NUMBER%" ^
                      --source-bundle S3Bucket="%S3_BUCKET%",S3Key="deployments/%ZIP_NAME%" ^
                      --region %AWS_DEFAULT_REGION%

                    aws elasticbeanstalk update-environment ^
                      --application-name "%EB_APP_NAME%" ^
                      --environment-name "%EB_ENV_NAME%" ^
                      --version-label "v-build-%BUILD_NUMBER%" ^
                      --region %AWS_DEFAULT_REGION%

                    echo Waiting for deployment...

                    aws elasticbeanstalk wait environment-updated ^
                      --application-name "%EB_APP_NAME%" ^
                      --environment-names "%EB_ENV_NAME%" ^
                      --region %AWS_DEFAULT_REGION%
                    """
                }

                echo "✅ Deployment completed"
            }
        }

        stage('Health Check') {
            steps {
                echo "🏥 Checking environment..."

                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {

                    bat """
                    echo ===== Environment Health =====

                    aws elasticbeanstalk describe-environments ^
                      --environment-names "%EB_ENV_NAME%" ^
                      --query "Environments[0].Health" ^
                      --output text ^
                      --region %AWS_DEFAULT_REGION%

                    echo.

                    echo ===== Application URL =====

                    aws elasticbeanstalk describe-environments ^
                      --environment-names "%EB_ENV_NAME%" ^
                      --query "Environments[0].CNAME" ^
                      --output text ^
                      --region %AWS_DEFAULT_REGION%
                    """
                }
            }
        }
    }

    post {

        success {
            echo "🎉 Pipeline SUCCESS - Build #${BUILD_NUMBER} deployed successfully."
        }

        failure {
            echo "❌ Pipeline FAILED."
        }

        always {
            bat """
            if exist %ZIP_NAME% del /f /q %ZIP_NAME%
            """
            echo "🧹 Cleaned up ZIP."
        }
    }
}
