package hla.rti1516e;
public final class RtiFactoryFactory {
    private RtiFactoryFactory() { }
    public static RtiFactory getRtiFactory() { return new RtiFactory(); }
    public static RtiFactory getRtiFactory(String ignored) { return new RtiFactory(); }
}
