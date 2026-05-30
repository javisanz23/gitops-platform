package main

# Solo permitir región eu-west-1
deny[msg] {
  input.resource.aws_instance[name].provider == "aws"
  not input.resource.aws_instance[name].availability_zone == "eu-west-1"
  msg := sprintf("Instancia '%v' debe estar en eu-west-1.", [name])
}

# S3 debe tener cifrado activado
deny[msg] {
  input.resource.aws_s3_bucket[name]
  not input.resource.aws_s3_bucket[name].server_side_encryption_configuration
  msg := sprintf("Bucket S3 '%v' debe tener cifrado activado.", [name])
}
