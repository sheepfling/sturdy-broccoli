package com.sheepfling.hla.shimroutes.rti1516e;

import py4j.GatewayServer;

public final class Py4JGatewayMain {
    private Py4JGatewayMain() {
    }

    public static void main(String[] args) {
        int port = 25333;
        for (int i = 0; i < args.length - 1; i++) {
            if ("--port".equals(args[i])) {
                port = Integer.parseInt(args[i + 1]);
            }
        }
        GatewayServer server = new GatewayServer(null, port);
        server.start();
        System.out.println("Java 2010 Standard Shim Py4J gateway listening on " + server.getListeningPort());
        System.out.flush();
    }
}
