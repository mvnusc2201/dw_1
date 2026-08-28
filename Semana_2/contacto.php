<html>
    <head>
        <title>Pagina principal</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    </head>

    <body>

        <!--Navbar -->
        <nav class="navbar navbar-expand-sm bg-dark navbar-dark">

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
                                <li><a class="dropdown-item" href="productos.php">Notebooks</a></li>
                                <li><a class="dropdown-item" href="productos.php">Periféricos</a></li>
                                <li><a class="dropdown-item" href="productos.php">Componentes</a></li>
                            </ul>

                        </li>

                        <li class="nav-item">
                            <a class="nav-link" href="servicios.php">Servicios</a>
                        </li>

                        <li class="nav-item">
                            <a class="nav-link" href="productos.php">Productos</a>
                        </li>

                        <li class="nav-item">
                            <a class="nav-link active" href="contacto.php">Contacto</a>
                        </li>

                    </ul>

                </div>

                <button type="button" class="btn btn-outline-primary">
                    <i class="fa fa-user"></i> Acceder
                </button>

            </div>

        </nav>


        <!--Container-->
        <div class="container-fluid bg-light p-5">

            <div class="container">

                <h1 class="text-center mb-2">
                    Contáctanos
                </h1>
                <div class="row">
                    </div>


                    <!-- Formulario -->
                    <div class="col-md-8">

                        <form action="empresa.php">


                            <div class="mb-3">

                                <label for="nombre" class="form-label">
                                    Nombre:
                                </label>

                                <input
                                    type="text"
                                    class="form-control"
                                    id="nombre"
                                    placeholder="Ingrese su nombre"
                                    name="nombre"
                                >

                            </div>


                            <div class="mb-3">

                                <label for="email" class="form-label">
                                    Email:
                                </label>

                                <input
                                    type="email"
                                    class="form-control"
                                    id="email"
                                    placeholder="Ingrese su correo electrónico"
                                    name="email"
                                >

                            </div>


                            <div class="mb-3">

                                <label for="motivo" class="form-label">
                                    Motivo de contacto:
                                </label>

                                <select class="form-select" id="motivo" name="motivo">

                                    <option>
                                        Seleccione una opción
                                    </option>

                                    <option>
                                        Consulta sobre un producto
                                    </option>

                                    <option>
                                        Problema con una compra
                                    </option>

                                    <option>
                                        Despacho
                                    </option>

                                    <option>
                                        Garantía
                                    </option>

                                    <option>
                                        Otro
                                    </option>

                                </select>

                            </div>


                            <div class="mb-3">

                                <label for="comment" class="form-label">
                                    Mensaje:
                                </label>

                                <textarea
                                    class="form-control"
                                    rows="5"
                                    id="comment"
                                    name="text"
                                    placeholder="Escriba su mensaje aquí..."
                                ></textarea>

                            </div>


                            <button type="button" class="btn btn-primary">
                                <i class="fa fa-send"></i> Enviar mensaje
                            </button>


                            <a href="index.php" class="btn btn-secondary">
                                <i class="fa fa-arrow-left"></i> Volver
                            </a>


                        </form>

                    </div>

                </div>

            </div>

        </div>


        <!--Footer-->
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
                        Tecnología al alcance de todos
                    </small>

                </div>

                <div class="col-4">
                </div>

            </div>

        </div>


        <!--Modal-->

    </body>

</html>