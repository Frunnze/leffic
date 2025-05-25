import { onCleanup, onMount } from "solid-js";
import Chart from "chart.js/auto";

export default function DoughnutDiagram(props) {
  let canvasRef;
  let chartInstance;

    onMount(() => {
        const ctx = canvasRef.getContext("2d");
        chartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: [props.data1Name ? props.data1Name: "Due", props.data2Name ? props.data2Name: "Done"],
                datasets: [
                {
                    data: [props.data1, props.data2],
                    backgroundColor: [
                        "rgba(57, 57, 58, 0.10)",
                        "#3083DC"
                    ],
                    borderColor: [
                        "rgba(57, 57, 58, 0.10)",
                        "#3083DC"
                    ],
                    borderWidth: 1
                }
                ]
            },
            options: {
                responsive: true,
                cutout: "50%",
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
            });
    });

    onCleanup(() => {
    chartInstance?.destroy();
    });

    return <canvas ref={canvasRef} />;
}
