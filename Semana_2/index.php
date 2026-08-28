<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Página principal</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    </head> 

    <body> 

        <!-- Navbar --> 
        <nav class="navbar navbar-expand-sm navbar-dark bg-dark"> 

            <div class="container-fluid"> 

                <a class="navbar-brand" href="index.php">
                    <i class="fa fa-laptop"></i> TechStore
                </a> 

                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#collapsibleNavbar"> 
                    <span class="navbar-toggler-icon"></span> 
                </button> 

                <div class="collapse navbar-collapse" id="collapsibleNavbar"> 

                    <ul class="navbar-nav"> 

                        <li class="nav-item dropdown"> 

                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                Categorías
                            </a> 

                            <ul class="dropdown-menu"> 

                                <li>
                                    <a class="dropdown-item" href="productos.php">
                                        Notebooks
                                    </a>
                                </li> 

                                <li>
                                    <a class="dropdown-item" href="productos.php">
                                        Periféricos
                                    </a>
                                </li> 

                                <li>
                                    <a class="dropdown-item" href="productos.php">
                                        Componentes
                                    </a>
                                </li> 

                            </ul> 

                        </li>                         

                        <li class="nav-item"> 
                            <a class="nav-link" href="productos.php">
                                Productos
                            </a> 
                        </li> 

                        <li class="nav-item"> 
                            <a class="nav-link" href="servicios.php">
                                Servicios
                            </a> 
                        </li> 

                        <li class="nav-item"> 
                            <a class="nav-link" href="contacto.php">
                                Contacto
                            </a> 
                        </li>                                                  

                    </ul> 

                </div>   

                <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#myModal">
                    <i class="fa fa-user"></i> Acceder
                </button>                

            </div> 

        </nav> 


        <!-- Container --> 
        <div class="container-fluid bg-light p-5"> 

            <div class="text-center">

                <h1>
                    Bienvenido a TechStore
                </h1>

                <p>
                    Encuentra los mejores productos tecnológicos calidad - precio.
                </p>

                <a href="productos.php" class="btn btn-primary">
                    Ver productos
                </a>

            </div>


            <hr class="my-5">


            <h2 class="text-center mb-4">
                Productos destacados
            </h2>


            <div class="row">


                <!-- Producto 1 -->
                <div class="col-md-3">

                    <div class="card">

                        <div class="card-body text-center">

                            <i class="fa fa-laptop fa-5x"></i>

                            <h5 class="card-title mt-3">
                                Notebook
                            </h5>

                            <p class="card-text">
                                i79700K<br>
                                16GB RAM<br>
                                RTX 4060
                            </p>

                            <h4>
                                $800.000
                            </h4>

                            <a href="productos.php" class="btn btn-primary">
                                Ver producto
                            </a>

                        </div>

                    </div>

                </div>


                <!-- Producto 2 -->
                <div class="col-md-3">

                    <div class="card">

                        <div class="card-body text-center">

                            <i class="fa fa-keyboard-o fa-5x"></i>

                            <h5 class="card-title mt-3">
                                Teclado Mecánico
                            </h5>

                            <p class="card-text">
                                Switch Red<br>
                                Iluminación RGB<br>
                                Wireless
                            </p>

                            <h4>
                                $80.000
                            </h4>

                            <a href="productos.php" class="btn btn-primary">
                                Ver producto
                            </a>

                        </div>

                    </div>

                </div>


                <!-- Producto 3 -->
                <div class="col-md-3">

                    <div class="card">

                        <div class="card-body text-center">

                            <i class="fa fa-headphones fa-5x"></i>

                            <h5 class="card-title mt-3">
                                Headset Gamer
                            </h5>

                            <p class="card-text">
                                Sonido 7.1<br>
                                Micrófono integrado<br>
                                Wireless
                            </p>

                            <h4>
                                $60.000
                            </h4>

                            <a href="productos.php" class="btn btn-primary">
                                Ver producto
                            </a>

                        </div>

                    </div>

                </div>


                <!-- Producto 4 -->
                <div class="col-md-3">

                    <div class="card">

                        <div class="card-body text-center">

                            <i class="fa fa-desktop fa-5x"></i>

                            <h5 class="card-title mt-3">
                                Monitor Samsung
                            </h5>

                            <p class="card-text">
                                24 pulgadas<br>
                                Full HD<br>
                                144 Hz
                            </p>

                            <h4>
                                $250.000
                            </h4>

                            <a href="productos.php" class="btn btn-primary">
                                Ver producto
                            </a>

                        </div>

                    </div>

                </div>

            </div>


            <div class="text-center mt-5">

                <h3>
                    <i class="fa fa-truck"></i>
                    Despacho rápido y seguro
                </h3>

                <p>
                    Envíos a todo Chile.
                </p>

            </div>

        </div> 


        <!-- Footer --> 
        <div class="container-fluid bg-dark p-3"> 

            <div class="row"> 

                <div class="col-4">
                </div> 

                <div class="col-4 text-center" style="color:white">

                    <strong>
                        TechStore © 2026
                    </strong>

                    <br>

                    <small>
                        Tu mejor tecnología
                    </small>

                </div> 

                <div class="col-4">
                </div> 

            </div> 

        </div> 


        <!-- Modal --> 
        <div class="modal fade" id="myModal"> 

            <div class="modal-dialog"> 

                <div class="modal-content"> 


                    <!-- Modal Header --> 
                    <div class="modal-header"> 

                        <h4 class="modal-title">
                            Iniciar sesión
                        </h4> 

                        <button type="button" class="btn-close" data-bs-dismiss="modal">
                        </button> 

                    </div> 


                    <!-- Modal body --> 
                    <div class="modal-body"> 

                        <form action="index.php"> 


                            <div class="mb-3 mt-3"> 

                                <label for="email" class="form-label">
                                    Correo electrónico:
                                </label> 

                                <input 
                                    type="email" 
                                    class="form-control" 
                                    id="email" 
                                    placeholder="Ingrese su correo" 
                                    name="email"
                                > 

                            </div> 


                            <div class="mb-3"> 

                                <label for="pwd" class="form-label">
                                    Contraseña:
                                </label> 

                                <input 
                                    type="password" 
                                    class="form-control" 
                                    id="pwd" 
                                    placeholder="Ingrese su contraseña" 
                                    name="pswd"
                                > 

                            </div> 


                            <div class="form-check mb-3"> 

                                <label class="form-check-label"> 

                                    <input 
                                        class="form-check-input" 
                                        type="checkbox" 
                                        name="remember"
                                    > 

                                    Recordarme

                                </label> 

                            </div> 


                            <button type="submit" class="btn btn-primary">
                                Ingresar
                            </button> 


                        </form> 

                    </div> 


                    <!-- Modal footer --> 
                    <div class="modal-footer"> 

                        <button type="button" class="btn btn-danger" data-bs-dismiss="modal">
                            Cerrar
                        </button> 

                    </div> 


                </div> 

            </div> 

        </div> 

    </body> 

</html>