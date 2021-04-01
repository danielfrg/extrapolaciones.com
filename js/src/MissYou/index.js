import { render } from "react-dom";
import React, { Fragment, useState } from "react";
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
        "Citrus_",
        "Classic",
        "Maple",
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
    let hiddenComps = null;
    if (equals(items2, solution)) {
        hiddenComps = <a href="/blog/2021/04/una-nit/">Una nit</a>;
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
            {hiddenComps}
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

const el = document.getElementById("react-miss-you-sortable");
if (el) {
    render(<App />, el);
}
