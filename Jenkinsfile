pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        EB_APP_NAME        = 'app2'
        EB_ENV_NAME        = 'App2-env'
        S3_BUCKET          = 'elasticbeanstalk-us-east-1-139822120014'

        VERSION_LABEL      = "v-build-${BUILD_NUMBER}"
        ZIP_NAME           = "beanstalk-deploy-${BUILD_NUMBER}.zip"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                bat '''
                git config --get core.autocrlf
                git status
                '''

                echo "Checkout completed."
            }
        }

        stage('Package') {
            steps {
                bat '''
                if exist "%ZIP_NAME%" del /f /q "%ZIP_NAME%"

                git archive --format=zip --output="%ZIP_NAME%" HEAD

                dir "%ZIP_NAME%"
                '''
            }
        }

        stage('Upload to S3') {
            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat '''
                    aws s3 cp "%ZIP_NAME%" s3://%S3_BUCKET%/deployments/%ZIP_NAME% --region %AWS_DEFAULT_REGION%
                    '''
                }
            }
        }

        stage('Create Application Version') {
            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat '''
                    aws elasticbeanstalk create-application-version ^
                      --application-name "%EB_APP_NAME%" ^
                      --version-label "%VERSION_LABEL%" ^
                      --source-bundle S3Bucket="%S3_BUCKET%",S3Key="deployments/%ZIP_NAME%" ^
                      --region %AWS_DEFAULT_REGION%
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat '''
                    aws elasticbeanstalk update-environment ^
                      --environment-name "%EB_ENV_NAME%" ^
                      --version-label "%VERSION_LABEL%" ^
                      --region %AWS_DEFAULT_REGION%

                    aws elasticbeanstalk wait environment-updated ^
                      --environment-names "%EB_ENV_NAME%" ^
                      --region %AWS_DEFAULT_REGION%
                    '''
                }
            }
        }

        stage('Health') {
            steps {

                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws']
                ]) {

                    bat '''
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
                    '''
                }
            }
        }
    }

    post {

        always {

            archiveArtifacts artifacts: '*.zip', fingerprint: true

            bat '''
            if exist "%ZIP_NAME%" del /f /q "%ZIP_NAME%"
            '''
        }

        success {
            echo 'Deployment completed.'
        }

        failure {
            echo 'Deployment failed.'
        }
    }
}
