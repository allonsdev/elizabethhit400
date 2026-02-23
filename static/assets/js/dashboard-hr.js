(function($) {
  'use strict';
  $(function() {
    if ($("#doughnutCharthr").length) { 
      const doughnutChartCrmCanvas = document.getElementById('doughnutCharthr');
      new Chart(doughnutChartCrmCanvas, {
        type: 'doughnut',
        data: {
          labels: [
            'Developers',
            'Marketing',
            'Finance',
            'Designing'
          ],
          datasets: [{
            data: [50, 20, 20, 10],
            backgroundColor: [
              "#1F3BB3",
              "#00CDFF",
              "#F95F53",
              "#00AAB6"
            ],
            borderColor: [
              "#fff",
              "#fff",
              "#fff",
              "#fff"
            ],
          }],
        },
        options: {
          cutout: 60,
          animationEasing: "easeOutBounce",
          animateRotate: true,
          animateScale: false,
          responsive: true,
          maintainAspectRatio: true,
          showScale: true,
          plugins: {
            legend: {
                display: false,
            }
          },
          responsive: true,
          maintainAspectRatio: false,
          tooltips: {
            backgroundColor: '#fff',
            titleFontSize: 14,
            titleFontColor: '#0B0F32',
            bodyFontColor: '#737F8B',
            bodyFontSize: 11,
            displayColors: false
          }
        }
      });
    }

    if ($("#projectEmployment").length) { 
      const ctx = document.getElementById('projectEmployment');
      var graphGradient = document.getElementById("projectEmployment").getContext('2d');
      var graphGradient2 = document.getElementById("projectEmployment").getContext('2d');
      var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
      saleGradientBg.addColorStop(0, 'rgba(42, 33, 186, 0.2)');
      saleGradientBg.addColorStop(1, 'rgba(42, 33, 186, 0)');
      var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
      saleGradientBg2.addColorStop(0, 'rgba(0, 205, 255, 0.2)');
      saleGradientBg2.addColorStop(1, 'rgba(0, 205, 255, 0)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["SUN","sun", "MON", "mon", "TUE","tue", "WED", "wed", "THU", "thu", "FRI", "fri", "SAT"],
          datasets: [{
              label: 'Project',
              data: [50, 110, 60, 290, 200, 115, 130, 170, 90, 210, 240, 280, 200],
              backgroundColor: saleGradientBg,
              borderColor: [
                  '#2A21BA',
              ],
              borderWidth: 1.5,
              fill: true, // 3: no fill
              pointBorderWidth: 1,
              pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
              pointHoverRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
              pointBackgroundColor: ['#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3','#1F3BB3'],
              pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff'],
          },{
            label: 'Bench',
            data: [30, 150, 190, 250, 120, 150, 130, 20, 30, 15, 40, 95, 180],
            backgroundColor: saleGradientBg2,
            borderColor: [
                '#52CDFF',
            ],
            borderWidth: 1.5,
            fill: true, // 3: no fill
            pointBorderWidth: 1,
            pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
            pointHoverRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
            pointBackgroundColor: ['#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF','#00CDFF'],
            pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff'],
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
        tooltips: {
            backgroundColor: 'rgba(31, 59, 179, 1)',
        },
        
          scales: {
            y: {
              border: {
                display: false
              },
              grid: {
                display: true,
                drawTicks: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 4,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            },
            x: {
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: false,
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        },
        plugins: [{
          afterDatasetUpdate: function (chart, args, options) {
              const chartId = chart.canvas.id;
              var i;
              const legendId = `${chartId}-legend`;
              const ul = document.createElement('ul');
              for(i=0;i<chart.data.datasets.length; i++) {
                  ul.innerHTML += `
                  <li>
                    <span style="background-color: ${chart.data.datasets[i].borderColor}"></span>
                    ${chart.data.datasets[i].label}
                  </li>
                `;
              }
              return document.getElementById(legendId).appendChild(ul);
            }
        }]
      });
    }
    if ($("#projectstatus").length) { 
      const projectstatusCanvas = document.getElementById('projectstatus');
      new Chart(projectstatusCanvas, {
        type: 'bar',
        data: {
          labels: ["JAN","FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
          datasets: [{
            label: 'Finished',
            data: [110, 220, 200, 190, 220, 110, 210, 110, 205, 202, 201, 150],
            backgroundColor: "#00CDFF",
            borderColor: [
                '#00CDFF',
            ],
            borderWidth: 0,
            fill: true, // 3: no fill
            barPercentage: 0.35,
              
          },{
            label: 'Pending',
            data: [215, 290, 210, 250, 290, 230, 290, 210, 280, 220, 190, 300],
            backgroundColor: "#1E3BB3",
            borderColor: [
                '#1E3BB3',
            ],
            borderWidth: 0,
            fill: true, // 3: no fill
            barPercentage: 0.35,
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
        tooltips: {
            backgroundColor: 'rgba(31, 59, 179, 1)',
        },
          scales: {
            y: {
              border: {
                display: false
              },
              display: true,
              grid: {
                display: true,
                drawBorder: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
              },
              ticks: {
                beginAtZero: true,
                autoSkip: true,
                maxTicksLimit: 5,
                fontSize: 10,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            },
            x: {
              border: {
                display: false
              },
              display: true,
              grid: {
                display: false,
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
                fontSize: 10,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              },
              stacked: true,
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        }
      });
    }

    if ($('#workingFormats').length) {

      var bar = new ProgressBar.Circle(workingFormats, {
        color: '#000',
        svgStyle: {
          strokeLinecap: 'round',
        },
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 10,
        trailWidth: 8,
        easing: 'easeInOut',
        duration: 1400,
        text: { 
          autoStyleContainer: false
        },
        from: {
          color: '#203BB3',
          width: 10,
          radius: 100,
        },
        to: {
          color: '#203BB3',
          width: 10
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '1.875rem';
      bar.text.style.fontWeight = 'bold';
      bar.animate(.30); // Number from 0.0 to 1.0
    }
    if ($('#acceptedApplications').length) {

      var bar = new ProgressBar.Circle(acceptedApplications, {
        color: '#fff',
        svgStyle: {
          strokeLinecap: 'round',
        },
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 10,
        trailWidth: 8,
        easing: 'easeInOut',
        duration: 1400,
        trailColor: 'rgba(255,255,255, .2)',
        text: { 
          autoStyleContainer: false
        },
        from: {
          color: '#00CDFF',
          width: 10,
          radius: 100,
        },
        to: {
          color: '#00CDFF',
          width: 10
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '1.875rem';
      bar.text.style.fontWeight = 'bold';
      bar.animate(.30); // Number from 0.0 to 1.0
    }
    if ($('#rejectedApplications').length) {
      var bar = new ProgressBar.Circle(rejectedApplications, {
        color: '#fff',
        svgStyle: {
          strokeLinecap: 'round',
        },
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 10,
        trailWidth: 8,
        easing: 'easeInOut',
        duration: 1400,
        trailColor: 'rgba(255,255,255, .2)',
        text: { 
          autoStyleContainer: false
        },
        from: {
          color: '#FFFFFF',
          width: 10,
          radius: 100,
        },
        to: {
          color: '#FFFFFF',
          width: 10
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '1.875rem';
      bar.text.style.fontWeight = 'bold';
      bar.animate(.20); // Number from 0.0 to 1.0
    }
    
  });

  
})(jQuery);