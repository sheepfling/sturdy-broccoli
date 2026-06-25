package hla.rti1516e.encoding;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class HLAvariableArray implements DataElement {
    private final List<DataElement> elements = new ArrayList<>();

    public HLAvariableArray(DataElement... initialElements) {
        elements.addAll(Arrays.asList(initialElements));
    }

    public byte[] toByteArray() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        out.writeBytes(ByteBuffer.allocate(4).putInt(elements.size()).array());
        for (DataElement element : elements) {
            out.writeBytes(element.toByteArray());
        }
        return out.toByteArray();
    }
}
