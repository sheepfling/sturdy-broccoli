package hla.rti1516e.encoding;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.List;

public class HLAfixedRecord implements DataElement {
    private final List<DataElement> elements = new ArrayList<>();

    public void add(DataElement element) {
        elements.add(element);
    }

    public byte[] toByteArray() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (DataElement element : elements) {
            out.writeBytes(element.toByteArray());
        }
        return out.toByteArray();
    }
}
