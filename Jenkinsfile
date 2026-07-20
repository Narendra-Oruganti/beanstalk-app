pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        EB_APP_NAME        = 'beanstalk-app'         // ← Your EB Application name
        EB_ENV_NAME        = 'beanstalk-app-env'      // ← Your EB Environment name
        S3_BUCKET          = 'elasticbeanstalk-us-east-1-139822120014'
        ZIP_NAME           = "beanstalk-deploy-${BUILD_NUMBER}.zip"
    }

    triggers {
        githubPush()
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
                echo "📦 Creating deployment ZIP (flat structure for Elastic Beanstalk)..."
                sh '''
                    zip -r ${ZIP_NAME} . \
                        --exclude "*.git*" \
                        --exclude "Jenkinsfile" \
                        --exclude "*.log"
                '''
                echo "✅ ZIP created: ${ZIP_NAME}"
            }
        }

        stage('Upload to S3') {
            steps {
                echo "☁️ Uploading ZIP to S3..."
                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID',     variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY',  variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        aws s3 cp ${ZIP_NAME} s3://${S3_BUCKET}/deployments/${ZIP_NAME} \
                            --region ${AWS_DEFAULT_REGION}
                    '''
                }
                echo "✅ Uploaded to s3://${S3_BUCKET}/deployments/${ZIP_NAME}"
            }
        }

        stage('Deploy to Elastic Beanstalk') {
            steps {
                echo "🚀 Deploying to Elastic Beanstalk..."
                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID',     variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY',  variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        # Create a new application version
                        aws elasticbeanstalk create-application-version \
                            --application-name "${EB_APP_NAME}" \
                            --version-label "v-build-${BUILD_NUMBER}" \
                            --source-bundle S3Bucket="${S3_BUCKET}",S3Key="deployments/${ZIP_NAME}" \
                            --region ${AWS_DEFAULT_REGION}

                        # Update the environment to use the new version
                        aws elasticbeanstalk update-environment \
                            --application-name "${EB_APP_NAME}" \
                            --environment-name "${EB_ENV_NAME}" \
                            --version-label "v-build-${BUILD_NUMBER}" \
                            --region ${AWS_DEFAULT_REGION}

                        echo "Waiting for environment to become ready..."
                        aws elasticbeanstalk wait environment-updated \
                            --application-name "${EB_APP_NAME}" \
                            --environment-names "${EB_ENV_NAME}" \
                            --region ${AWS_DEFAULT_REGION}
                    '''
                }
                echo "✅ Deployment complete!"
            }
        }

        stage('Health Check') {
            steps {
                echo "🏥 Checking environment health..."
                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID',     variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY',  variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        STATUS=$(aws elasticbeanstalk describe-environments \
                            --environment-names "${EB_ENV_NAME}" \
                            --query "Environments[0].Health" \
                            --output text \
                            --region ${AWS_DEFAULT_REGION})
                        echo "Environment Health: ${STATUS}"

                        URL=$(aws elasticbeanstalk describe-environments \
                            --environment-names "${EB_ENV_NAME}" \
                            --query "Environments[0].CNAME" \
                            --output text \
                            --region ${AWS_DEFAULT_REGION})
                        echo "App URL: http://${URL}"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline SUCCESS — Build #${BUILD_NUMBER} deployed to Elastic Beanstalk!"
        }
        failure {
            echo "❌ Pipeline FAILED — Check logs above for details."
        }
        always {
            sh 'rm -f ${ZIP_NAME}'
            echo "🧹 Cleaned up ZIP file."
        }
    }
}
