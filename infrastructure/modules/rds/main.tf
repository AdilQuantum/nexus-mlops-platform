resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-rds-subnet-group"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_db_instance" "main" {
  identifier        = "${var.project_name}-postgres"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "mlflow"
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_sg_id]

  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 7

  # Stop instance when not needed to save cost
  # manually stop from AWS console when not working

  tags = {
    Name        = "${var.project_name}-rds"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}