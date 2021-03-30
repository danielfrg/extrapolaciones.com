import { render } from "react-dom";
import React, { useState } from "react";
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
} from "@dnd-kit/core";
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    verticalListSortingStrategy,
} from "@dnd-kit/sortable";

import { SortableItem } from "./SortableItem";
import "./index.scss";

function App() {
    const solution = ["Maple", "Citrus", "Rose", "Classic", "Citrus"];
    const [items, setItems] = useState([
        "Citrus",
        "Classic",
        "Maple",
        "Citrus_",
        "Rose",
    ]);
    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const equals = (a, b) =>
        a.length === b.length && a.every((v, i) => v === b[i]);

    const items2 = items.map((x) => x.replace("_", ""));
    console.log(items2);
    if (equals(items2, solution)) {
        console.log("WIN");
    }

    return (
        <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
        >
            <h3>Ordenar las palabras</h3>
            <SortableContext
                items={items}
                strategy={verticalListSortingStrategy}
            >
                {items.map((id, i) => (
                    <SortableItem key={id} id={id} text={id} />
                ))}
            </SortableContext>
        </DndContext>
    );

    function handleDragEnd(event) {
        const { active, over } = event;

        if (active.id !== over.id) {
            setItems((items) => {
                const oldIndex = items.indexOf(active.id);
                const newIndex = items.indexOf(over.id);

                return arrayMove(items, oldIndex, newIndex);
            });
        }
    }
}

render(<App />, document.getElementById("react-miss-you-sortable"));
