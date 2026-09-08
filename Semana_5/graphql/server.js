require("dotenv").config();

const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const { ApolloServer } = require("@apollo/server");
const { expressMiddleware } = require("@as-integrations/express5");

const Cliente = require("./models/clientes");

const typeDefs = `#graphql
    type Cliente {
        id: ID!
        nombre: String!
        email: String!
        telefono: String
    }

    type Query {
        clientes: [Cliente!]!
        cliente(id: ID!): Cliente
        totalClientes: Int!
    }

    type Mutation {
        agregarCliente(
            nombre: String!
            email: String!
            telefono: String
        ): Cliente!

        actualizarCliente(
            id: ID!
            nombre: String
            email: String
            telefono: String
        ): Cliente

        eliminarCliente(id: ID!): Boolean!
    }
`;

const resolvers = {
    Query: {
        clientes: async () => {
            return await Cliente.find();
    },
    cliente: async (_, { id }) => {
        return await Cliente.findById(id);
    },
    totalClientes: async () => {
        return await Cliente.countDocuments();
    }
},
    Mutation: {
        agregarCliente: async (_, { nombre, email, telefono }) => {
            const cliente = new Cliente({
                nombre,
                email,
                telefono
            });

            return await cliente.save();
        },

        actualizarCliente: async (_, { id, ...datos }) => {
            return await Cliente.findByIdAndUpdate(
                id,
                datos,
                {
                    new: true,
                    runValidators: true
                }
            );
        },

        eliminarCliente: async (_, { id }) => {
            const cliente = await Cliente.findByIdAndDelete(id);
            return cliente !== null;
        }
    }
};

async function iniciarServidor() {
    await mongoose.connect(
        process.env.MONGO_URI || "mongodb://127.0.0.1:27017/UNAB"
    );

    console.log("Conectado a MongoDB");

    const app = express();

    const server = new ApolloServer({
        typeDefs,
        resolvers
    });

    await server.start();

    app.use(
        "/graphql",
        cors(),
        express.json(),
        expressMiddleware(server)
    );

    const PORT = process.env.PORT || 4000;

    app.listen(PORT, () => {
        console.log(`Servidor en http://localhost:${PORT}/graphql`);
    });
}

iniciarServidor().catch((error) => {
    console.error("Error al iniciar el servidor:", error);
    process.exit(1);
});
