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
                echo "✅ Code checked out from GitHub"
            }
        }

        stage('Package') {
            steps {
                echo "📦 Creating deployment ZIP..."

                bat """
                if exist "%ZIP_NAME%" del /f /q "%ZIP_NAME%"

                powershell -Command ^
                "Compress-Archive -Path * -DestinationPath '%ZIP_NAME%' -Force"
                """

                echo "✅ ZIP Created: ${ZIP_NAME}"
            }
        }

        stage('Upload to S3') {
            steps {
                echo "☁️ Uploading ZIP to S3..."

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat """
                    aws s3 cp "%ZIP_NAME%" s3://%S3_BUCKET%/deployments/%ZIP_NAME% --region %AWS_DEFAULT_REGION%
                    """
                }

                echo "✅ Upload Complete"
            }
        }

        stage('Deploy to Elastic Beanstalk') {
            steps {
                echo "🚀 Deploying..."

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
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

                echo "✅ Deployment Finished"
            }
        }

        stage('Health Check') {
            steps {
                echo "🏥 Checking Environment..."

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat """
                    echo ===== HEALTH =====

                    aws elasticbeanstalk describe-environments ^
                      --environment-names "%EB_ENV_NAME%" ^
                      --query "Environments[0].Health" ^
                      --output text ^
                      --region %AWS_DEFAULT_REGION%

                    echo.

                    echo ===== URL =====

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
            echo "🎉 Deployment Successful!"
        }

        failure {
            echo "❌ Deployment Failed!"
        }

        always {
            bat """
            if exist "%ZIP_NAME%" del /f /q "%ZIP_NAME%"
            """
            echo "🧹 Workspace Cleaned"
        }
    }
}
