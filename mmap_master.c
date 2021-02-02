#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

//  レジスタブロックの物理アドレス
#define PERI_BASE     0xFE000000        //  0xFE000000 for RPi4

//GPIOレジスタを指定
#define GPIO_BASE     (PERI_BASE + 0x200000)

#define BLOCK_SIZE    4096

//  gpio[n]: GPIO 関連レジスタ 物理アドレス (volatile＝必ず実メモリにアクセスさせる)
static volatile unsigned int *Gpio = NULL;

//  gpio_init: GPIO 初期化（最初に１度だけ呼び出すこと）
void gpio_init ()
{
    //  既に初期化済なら何もしない
    if (Gpio) return;

        //  ここから GPIO 初期化
    int fd;

        //仮想メモリのアドレスを格納する変数の定義
    void *gpio_map;

        // /dev/mem（物理メモリデバイス）を開く（sudo が必要）
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        printf("error: cannot open /dev/mem (gpio_setup)\n");
        exit(-1);
    }
    // mmap で GPIO（物理メモリ）を gpio_map（仮想メモリ）に対応づける
    gpio_map = mmap(NULL, BLOCK_SIZE,
                    PROT_READ | PROT_WRITE, MAP_SHARED,
                    fd, GPIO_BASE );

    if ((int) gpio_map == -1) {
        printf("error: cannot map /dev/mem on the memory (gpio_setup)\n");
        exit(-1);
    }

    //  mmap 後は不要な fd をクローズ
    close(fd);

    //  Gpio[index]: 整数 uint32 の配列としてレジスタへのアクセスを確立
    Gpio = (unsigned int *) gpio_map;
}

// ピン機能（BCM2835）
#define GPIO_INPUT    0x0       //  入力
#define GPIO_OUTPUT   0x1       //  出力
#define GPIO_ALT0     0x4
#define GPIO_ALT1     0x5
#define GPIO_ALT2     0x6
#define GPIO_ALT3     0x7
#define GPIO_ALT4     0x3
#define GPIO_ALT5     0x2

//  gpio_configure: ピン機能を設定する（ピンを使用する前に必ず設定）
//  pin : (P1) 2,3,4,7,8,9,10,11,14,15,17,18,22,23,24,25,27
//        (P5) 28,29,30,31
//  mode: GPIO_INPUT, _OUTPUT, _ALT0, _ALT1, _ALT2, _ALT3, _ALT4, _ALT5
void gpio_configure (int pin, int mode)
{
    //  ピン番号チェック
    if (pin < 0 || pin > 31) {
        printf("error: pin number out of range (gpio_configure)\n");
        exit(-1);
    }
    //  レジスタ番号（index）と３ビットマスクを生成
    //  例えば17を10で割ると１、番目のレジスタを意味する
    int index = pin / 10;
    unsigned int mask = ~(0x7 << ((pin % 10) * 3));
    //  GPFSEL0/1 の該当する FSEL (3bit) のみを書き換え
    Gpio[index] = (Gpio[index] & mask) | ((mode & 0x7) << ((pin % 10) * 3));
}

//  gpio_set/clear: ピンをセット (3.3V)，クリア (0V)
void gpio_set (int pin)
{
    //  ピン番号チェック（スピードを追求するなら省略してもよい）
    if (pin < 0 || pin > 31) {
        printf("error: pin number out of range (gpio_set)\n");
        exit(-1);
    }
    //  ピンに１を出力（3.3V 出力）
    Gpio[7] = 0x1 << pin;   //  GPSET0
}
void gpio_clear (int pin)
{
    //  ピン番号チェック（スピードを追求するなら省略してもよい）
    if (pin < 0 || pin > 31) {
        printf("error: pin number out of range (gpio_clear)\n");
        exit(-1);
    }
    //  ピンに０を出力（0V 出力）
    Gpio[10] = 0x1 << pin;  //  GPCLR0
}

int main (int argc, char *argv[])
{
    gpio_init();                        // GPIO初期化 
    //printf("GPIO10-19 Config %o\n", Gpio[1]);
    gpio_configure(27, GPIO_OUTPUT);    //  GPIO_27 を出力に設定


    while (1) {
        gpio_set(27);                   //  1 を出力（3.3V）
        usleep(500000);                 //  0.5秒待ち
        gpio_clear(27);                 //  0 を出力（0V）
        usleep(500000);                 //  0.5秒待ち
    }

    //printf("GPIO10-19 Config %o\n", Gpio[1]);
    //printf("GPIO20-29 Config %o\n", Gpio[2]);
    //printf("GPIO0-9 Config %o\n", Gpio[0]);
    //printf("GPIO30-39 Config %o\n", Gpio[3]);
    //printf("GPIO40-49 Config %o\n", Gpio[4]);

    return 123;
}
