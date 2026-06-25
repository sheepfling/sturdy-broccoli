package hla.rti1516e.encoding;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class HLAfixedArray implements DataElement {
    private final List<DataElement> elements = new ArrayList<>();

    public HLAfixedArray(DataElement... initialElements) {
        elements.addAll(Arrays.asList(initialElements));
    }

    public byte[] toByteArray() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (DataElement element : elements) {
            out.writeBytes(element.toByteArray());
        }
        return out.toByteArray();
    }
}
