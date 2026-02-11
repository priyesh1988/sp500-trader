// Jenkinsfile
pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    AWS_REGION            = 'us-west-2'
    ECR_REPOSITORY        = 'sp500-trader'
    APP_RUNNER_SERVICE_ARN= 'arn:aws:apprunner:us-west-2:123456789012:service/sp500-trader/xxxxxxxxxxxxxxxx'

    // Jenkins credentials IDs (create these in Jenkins > Manage Credentials):
    // - aws-access-key-id:     Secret text (or Username/Password)
    // - aws-secret-access-key: Secret text
    // - aws-account-id:        Secret text (12-digit AWS account ID)
    AWS_ACCESS_KEY_ID     = credentials('aws-access-key-id')
    AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    AWS_ACCOUNT_ID        = credentials('aws-account-id')

    ECR_REGISTRY          = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    IMAGE_URI             = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
    IMAGE_TAG             = "${env.GIT_COMMIT}".take(12)
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Sanity (Python import)') {
      agent {
        docker { image 'python:3.12-slim' }
      }
      steps {
        sh '''
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -c "import app.main; print('Import OK')"
        '''
      }
    }

    stage('ECR Login') {
      steps {
        sh '''
          aws --version
          aws ecr get-login-password --region "$AWS_REGION" \
            | docker login --username AWS --password-stdin "$ECR_REGISTRY"
        '''
      }
    }

    stage('Build Image') {
      steps {
        sh '''
          docker build -t "$IMAGE_URI:$IMAGE_TAG" -t "$IMAGE_URI:latest" .
        '''
      }
    }

    stage('Push Image') {
      steps {
        sh '''
          docker push "$IMAGE_URI:$IMAGE_TAG"
          docker push "$IMAGE_URI:latest"
        '''
      }
    }

    stage('Deploy (App Runner)') {
      steps {
        sh '''
          aws apprunner start-deployment --service-arn "$APP_RUNNER_SERVICE_ARN"
        '''
      }
    }

    stage('Wait for RUNNING') {
      steps {
        sh '''
          echo "Waiting for App Runner service to be RUNNING..."
          for i in $(seq 1 60); do
            STATUS=$(aws apprunner describe-service --service-arn "$APP_RUNNER_SERVICE_ARN" --query "Service.Status" --output text)
            echo "Status: $STATUS"
            if [ "$STATUS" = "RUNNING" ]; then
              echo "Deployment complete."
              exit 0
            fi
            sleep 10
          done
          echo "Timed out waiting for service to become RUNNING."
          exit 1
        '''
      }
    }
  }

  post {
    always {
      sh 'docker logout "$ECR_REGISTRY" || true'
      sh 'docker system prune -af || true'
    }
  }
}
