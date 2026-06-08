using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Minesweeper
{
    public partial class form1 : form                                   //создание класса form1 из библеотеки WinForms 
    {
        public const int mapSize = 8;
        public const int cellSize = 50;                                   //Размерность карты, размер клетки

        public int[,] map = new int[mapSize,mapSize];                    //создание карты
        public Button[,] buttons = new Button[mapSize,mapSize];         //массив для хранения кнопок на карте (Windows.Forms)
    
        public Form1()                                                  //инициализация проекта(формы)
        {
            IntializeComponent();

            Init();
        }
        private void Init()
        {
            ConfigureMapSize();
            InitMap();
            InitButtons();
        }

        private void ConfigureMapSize()
        {
            this.Width = mapSize *cellSize + 20;
            this.Height = mapSize * cellSize;

        }
        private void InitMap()                                            //инициализация карты
        {
            for(int i = 0; i < mapSize; i++)
            {
                for(int j = 0; j < mapSize;j++)
                {
                    map[i,j] = 0;
                }
            }
        }


        private void InitButtons()                                          //инициализация кнопок
        {
            for(int i = 0; i < mapSize;i++)
            {
                for(int j = 0; j < mapSize;j++)
                {
                    buttons button = new buttons();
                    button.locaton = new Point(j*cellsize,i*cellSize);      //определение позиции и размера кнопки
                    button.size = new Size(cellsize,cellsize);
                    this.Controls.Add(button);
                    map[i,j] = button;
                }
            }
        }
    }













}
